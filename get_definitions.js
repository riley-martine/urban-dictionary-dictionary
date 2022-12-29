"use strict";

// I copied and adapted this file from somewhere, but I can't figure out where.
// I'm super sorry about not having correct attribution!
// If you know, or this was yours, please let me know so I can fix that.

const fs = require('fs');
const readline = require('readline');
const process = require('process');
const https = require('https');

const API = 'https://api.urbandictionary.com/v0/define';

const MIN_TOP_VOTES = 50; // Number of votes top definition must have, for word to be printed
const MIN_DEF_VOTES = 10; // Number of votes any definition must have to be printed

/**
 * Re-write response in c5 dict format and print it out, if notability conditions met.
*/
function processResponse(word, data) {
    var out = "_____\n\n" + word.trim();
    data.list.sort((a,b) => a.thumbs_up < b.thumbs_up)
    if (data.list[0].thumbs_up < MIN_TOP_VOTES) {
        return;
    }
    data.list.forEach(function(def, i){
       if (def.thumbs_up > MIN_DEF_VOTES) {
       out = out + "\n\t" + `(${def.written_on.slice(0,10)} +${def.thumbs_up}/-${def.thumbs_down})`
            + "\n\t" + def.definition.replace(/\n/g, "\n\t")
            + "\n\t\tExample: " + def.example.replace(/\n/g, "\n\t\t") + "\n";

    }});
    console.log(out);
}

/**
 * Hit the UD API to grab the word definition.
*/
async function getDefinition(word) {
    return new Promise((resolve, reject) => {
        const url = API+"?term="+encodeURIComponent(word);
        https.get(url,
            (res) => {
                if (res.statusCode != 200) {
                    reject('Request failed for ' + word + '. status: ' + res.statusCode);
                }
                let rawData = '';
                res.on('data', (chunk) => (rawData += chunk));
                res.on('end', () => {
                    try {
                        resolve(processResponse(word, JSON.parse(rawData)));
                    } catch (error) {
                        console.error(`Error with ${word}: ${url}`);
                        console.error(error);
                        // We resolve bc there are GOING to b errors
                        // And we would rather check them all at the end
                        resolve();
                    }
                });
            }).on('error', () => {
                console.error(`Error with ${word}: ${url}`);
                console.error(error);
                // We resolve bc there are GOING to b errors
                // And we would rather check them all at the end
                resolve();
            });
    });
}

// https://stackoverflow.com/questions/54901078/async-task-manager-with-maximum-number-of-concurrent-running-tasks
class TaskManager {
    constructor(capacity) {
        this.capacity = capacity;
        this.waiting = [];
        this.running = [];
    }
    push(tk) {
        this.waiting.push(tk);
        if (this.running.length < this.capacity) {
            this.next();
        }
    }
    next() {
        const task = this.waiting.shift();
        if (!task) {
            return; // No new tasks
        }
        this.running.push(task);
        const runningTask = getDefinition(task);
        runningTask.then(() => {
            this.running = this.running.filter(t => t !== task);
            this.next();
        }).catch(error => {
            console.error(error);
        });
    }
}

/**
 * Download all entries for a single letter.
*/
async function processData(file) {
    const lineReader = readline.createInterface({
        input: fs.createReadStream(file)
    });

    const manager = new TaskManager(20);
    for await (const line of lineReader) {
        manager.push(line);
    }
}

const files = process.argv.slice(2);
if (!files.length) {
    console.error('No files provided. Provide a single file.');
} else {
    processData(files[0]);
}
