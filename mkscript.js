#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const config = {

    // End each new script with a blank line after the headers
    endWithBlankline: true,

    // Set +x on each created file
    // This doesn't fail on Windows, but doesn't do anything either
    setExecutable: true,

    // Create symbolic link after the new script is created
    // Loudly complains if set to true on Windows
    symlink: {
        create: true,
        location: "~/.local/bin",
    },

    // The top few lines for each type of supported script
    headers: {
        py: [
            "#!/usr/bin/env python3",
            "# -*- coding: utf-8 -*-",
        ],
        rb: [
            "#!/usr/bin/env ruby",
            "# encoding: UTF-8",
        ],
        js: [
            "#!/usr/bin/env node",
            "\"use strict\";"
        ],
        sh: [
            "#!/bin/bash", // /usr/local/bin/bash on *bsd
        ],
    }
}

/**
 * Create a file named scriptName, fill the first few lines
 * with data from headers[], and make it executable.
 * 
 * @param {String} scriptName: name of the file to create.
 * @returns {Boolean} true on file written.
 */
function makeScript(scriptName) {

    // Make sure file doesn't exist
    fs.stat(scriptName, (err, stat) => {
        if (err) {
            // Get specified extension
            const scriptExt = path.extname(scriptName).substr(1);

            // See if that type of script is supported
            if (!config.headers.hasOwnProperty(scriptExt)) {
                console.error(`${process.argv0}: Unknown filetype ${scriptName}`);
                return false;
            }

            // Does directory exist?
            fs.stat(path.dirname(scriptName), (err, stat) => {
                if (err) {
                    console.error(`${process.argv0}: ${path.dirname(scriptName)} doesn't exist`);
                    return false;
                }
                else {
                    // Is it writable?
                    fs.access(path.dirname(scriptName), fs.constants.W_OK, (err) => {
                        if (err) {
                            console.error(`${process.argv0}: directory not writable`);
                            return false;
                        }
                        else
                            writeFile(scriptName);
                    });
                }
            }); 
        }
        else {
            console.error(`${process.argv0}: File '${scriptName}' exists already`);
            return false;
        }
    });

    // Actually write the file
    function writeFile(name) {
        const ext = path.extname(name).substr(1);
        let data = config.headers[ext].join("\n");

        data += "\n";
        if (config.endWithBlankline) {
            data += "\n";
        }

        fs.writeFile(name, data, err => {
            if (!err && config.setExecutable) {
                fs.chmod(name, "755", err => {
                    if (!err && config.symlink.create) {
                        createSymlink(name);
                    }
                });
            }
        });
    }

    // Create symlink
    function createSymlink(name) {
        if (process.platform === "win32") {
            console.error(`${process.argv0}: Stubbornly refusing to create symlink ${name} on Windows"`);
        }
        else {
            // Get absolute path of newly created script
            const fullPath = path.join(path.resolve(path.dirname(name)), name);
            
            // Remove extension from filename
            const nameSansExt = path.basename(name, path.extname(name));

            // Get path of where to put the symlink
            const linkPath = path.join(
                config.symlink.location.replace("~", process.env["HOME"]), // expand tilde
                path.basename(name, path.extname(name)) // remove extension
            )

            fs.symlink(fullPath, linkPath, (err) => {
                if (err) {
                    console.error(`${process.argv0}: error: ${err.message}`);
                    return false;
                }
                else {
                    console.log(`${process.argv0}: Created ${linkPath} -> ${fullPath}`);
                    return true;
                }
            });
        }
    }
}

/**
 * Print usage information
 */
function usage() {
    console.error(`Usage: ${process.argv0} <script_name.sh>`);
    return -1;
}

/**
 * Program entry point: Lazily parse command line and either
 * call makeScript() or call usage().
 */
if (typeof module !== "undefined" && !module.parent) {
    if (process.argv.length < 3)
        process.exit(usage());

    const nodePath = process.argv.shift();
    const thisPath = process.argv.shift();

    let scriptName = "";
    while (scriptName = process.argv.shift())
        makeScript(scriptName);
}