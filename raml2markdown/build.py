#!/usr/bin/env python3

import os
import re
import shutil
from pathlib import Path

# Array of APIs. Call API_Raml_to_Slate(apiname) for each. Expected: API RAML file in
# folder which is the api name.
#
# Inside that folder must be .raml file with the same name.
# Example: ./src/product-api/product-api.raml
APIS = [
    "broker-api",
    "calendar-api",
    "context-api",
    "identity-api",
    "message-api",
    "product-api",
]


def api_raml_to_slate(apiname):
    json_file = Path("./OAS/" + apiname + ".json")
    slate_file = Path("./slate/" + apiname + ".md")

    print("Converting " + apiname + " to Slate")

    # Delete previous API docs
    if json_file.exists():
        os.remove(json_file)

    if slate_file.exists():
        os.remove(slate_file)

    # Generate API docs. First convert RAML -> OpenAPISpec file
    converter = "./node_nodules/.bin/oas-raml-converter"
    raml = f"./src/{apiname}/{apiname}.raml"
    cmd = f"{converter} --from RAML --to OAS20 {raml} > {json_file}"

    if os.system(cmd):
        print("RAML -> OpenAPISpec failed. Trying next in array.")
    else:
        # Convert from OpenAPISpec to Slate md
        swagger_to_slate = "./node_modules/.bin/swagger-to-slate"
        slate_cmd = f"{swagger_to_slate} -i {json_file} -o {slate_file}"
        if os.system(slate_cmd):
            print("RAML -> Slate formatted md file creation failed.")


# Generate path according to code examples location pattern:
def get_generated_code_examples_path(root, line, api):
    line = line.rstrip(os.linesep)
    line = re.sub("[`*]", "", line)
    line_arr = line.split(" ")
    # parse HTTP method
    method = line_arr[0]
    # convert forward slashes to underscores to match code examples file path
    if len(line_arr) > 1:
        filename = re.sub("[/]", "_", line_arr[1])
    else:
        filename = ""

    return Path("/".join([root, api, api + ".raml", filename, method, "slate.md"]))


def path_to_name(path):
    return path.replace("-", " ").replace("api", "API").capitalize()


def concatenate_files(code_examples_path):
    out_file = "../source/index.html.md"
    with Path(out_file).open("w") as dst:
        with Path("slate/index.md").open() as src:
            dst.write(src.read())
        for api in APIS:
            slatefile = Path("./slate/" + api.lower() + ".md")
            spec = f"./specs/oas/{api}.json"
            zip = f"./specs/raml/{api}.zip"

            api_name = path_to_name(api)
            dst.write(f"# {api_name}\n\n")
            dst.write(f"> **Get {api_name} related resources:**\n\n")
            dst.write(
                "> <div class='hexagon'><div class='hexagon-inside'><div class='hexagon-inside2'>"
            )
            dst.write(
                f"<a href='{spec}' title='Get OpenAPI Specification Resources'>"
            )
            dst.write("<img src='images/oas.png' class='openApiSpec-lg'>")
            dst.write("</a></div></div></div>\n")

            dst.write(
                "> <div class='hexagon'><div class='hexagon-inside'><div class='hexagon-inside2'>"
            )
            dst.write(
                f"<a "
                f"href='{zip}' "
                f"title='Get RAML Specification Resources'>"
            )
            dst.write("<img src='images/raml.png' class='ramlSpec-lg'>")
            dst.write("</a></div></div></div>\n")

            src = open(slatefile, "r").readlines()
            for index, line in enumerate(src):

                # Now match the lines after which the code examples are injected.
                # example of one line: `***PUT*** /products/{product_code}`
                # That should match product-api_PUT_product_code.curl in examples folder
                copyline = str(line)

                example_method = str(line)
                example_method = re.sub("[`#*]", "", example_method)

                example_file_path = get_generated_code_examples_path(
                    code_examples_path, str(line), api.lower()
                )

                example_desc = (
                    "\n\n > <b>Example for: "
                    + example_method.replace("{version}", "v1")
                    + "</b>\n\n"
                )
                if len(str(example_file_path)) < 200:
                    if example_file_path.exists():
                        with open(example_file_path) as example_file:
                            print(
                                "Found example file: "
                                + str(example_file_path)
                                + " derived from line:"
                                + copyline
                            )
                            dst.write(example_desc)
                            dst.write(example_file.read() + "\n\n")

                # Ugly way of getting rid of some markup in the beginning of each file.
                # Get everything after line 18 and save to final markdown file
                if index > 18:
                    # Some markdown cleanup since the converters mess things up
                    if line.startswith("#"):
                        dst.write(
                            "#"
                            + line.lower()
                            .replace("***", "**")
                            .replace("{version}", "v1")
                        )
                    elif line.startswith("`***"):
                        dst.write(
                            line.replace("***", "**")
                                .replace("`", "")
                                .replace("{version}", "v1")
                        )
                    else:
                        dst.write(
                            line.replace("***", "**").replace("{version}", "v1")
                        )
    print(f"\n\nSlate file: {out_file} created.")


def make_html():
    cmd = "cd .. & bundle exec middleman build"
    if os.system(cmd):
        print("HTML build failed")
    else:
        print("\n\nHTML generated successfully.")


def copy_specs_to_build():
    # make directory
    # define the name of the directory to be created
    path = "../build/specs/oas"
    os.makedirs(path)

    # Copy oas spec file to build release as well
    for api in APIS:
        src_path = "./OAS/" + api + ".json"
        shutil.copy2(src_path, "../build/specs/oas")  # target filename preserved

    # Make zips for RAML in the build folder /build/specs/raml.
    ramlpath = "../build/specs/raml"

    os.makedirs(ramlpath)

    print("Successfully created the directory %s" % path)
    for api in APIS:
        src_path = "./src/" + api
        shutil.make_archive(ramlpath + "/" + api, "zip", src_path)


def main():
    os.makedirs("slate")
    os.makedirs("OAS")

    print(f"Reading examples from {os.environ['CODE_EXAMPLES']}")

    for api in APIS:
        api_raml_to_slate(api)

    concatenate_files(os.environ["CODE_EXAMPLES"])
    make_html()
    copy_specs_to_build()


if __name__ == "__main__":
    main()
