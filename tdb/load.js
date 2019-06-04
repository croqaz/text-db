// Node.js attempt
const fs = require('fs')
const readline = require('readline')

const KEY_SEP = '-'


function load_db_file(file_name, keys = [], config = {}) {
    const local_db = {}
    const lineReader = readline.createInterface({
        input: fs.createReadStream(file_name)
    })
    console.log(`Loading lines from "${file_name}" ...`)
    console.time('loadDB')

    lineReader.on('line', function (line) {
        line = line.trim()
        if (line.length < 1) {
            return
        }
        const item = JSON.parse(line)
        const k = default_gen_key(item, keys)
        local_db[k] = item
    }).on('close', function () {
        console.log(`\nLoaded ${Object.keys(local_db).length} items`)
        console.timeEnd('loadDB')
    })
}

function default_gen_key(item, keys) {
    if (keys.length > 0) {
        return keys.map(k => item[k]).join(KEY_SEP)
    } else {
        return JSON.stringify(item)
    }
}

// Python
// Loading 600,676 lines from "../DATA/some-data.jl" ...
// Loaded 300,237 items, added 300,237 new items in 7.37s
// Node.js
// Loaded 300,237 items
// loadDB: 9379.640ms
