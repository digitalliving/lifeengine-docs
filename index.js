const raml2html = require('raml2html')
const path = require('path')
const fs = require('fs')
const { promisify } = require('util')

// const options = { 'template-dir': 'templates' }
// const themeConfig = raml2html.getConfigForTheme('raml2html-werk-theme', options)

const readDirAsync = promisify(fs.readdir)
const writeFileAsync = promisify(fs.writeFile)

const themeOptions = {
  logo: './images/logo.png',
  // 'color-theme': 'path/to/my/color-theme.styl',
  'language-tabs': ['json']
}

const themeConfig = raml2html.getConfigForTheme('raml2html-slate-theme', themeOptions);

const CONFIGURATION = {
  apisPath: path.join(__dirname, 'apis'),
  // Validate RAML, but it causes errors currently.
  validate: false
};

(async (config) => {
  const renderHTML = async (api) => {
    return raml2html.render(api, themeConfig, { validate: config.validate })
  }

  const print = (data, method) => {
    if (typeof method !== 'string') {
      method = 'log'
    }
    if (typeof data === 'object') {
      data = JSON.stringify(data, null, 2)
    }

    console[method](data)
  }
  const generateAPIPath = (api, fileName) => {
    return `${config.apisPath}/${api}/docs/${fileName}`
  }
  print('Running with configuration:', 'info')
  print(config)
  const apis = await readDirAsync(config.apisPath)

  print(`\nFound APIs: ${apis}`)

  for await (const api of apis) {
    print(`\nProcessing ${api} API ...`)

    const ramlPath = generateAPIPath(api, 'api.raml')
    const html = await renderHTML(ramlPath)

    const indexPath = generateAPIPath(api, 'index.html')

    await writeFileAsync(indexPath, html)

    print(`The file ${indexPath} was saved!`)
  }
})(CONFIGURATION)
