#!/usr/bin/env node
"use strict";

/**
 * I wanted an upgraded version of ./rofi-chrome.sh with support for a bunch
 * of different types of input and various niceties.
 * 
 * The main nicety I wanted was a place to add "staticEntries" text and result
 * in a single line of code. Everything else is secondary.
 * 
 * This is the result-in-progress.
 */

// Let Me Rofi That For Myself?
// Let Me Read The Fine Manual?

/**
 * ideas:
 * - use ~/.cache/database.sqlite or something to save previous typed entries
 * - use "ff: blah" to search for "blah" in firefox ("cr:" for chrome, etc)
 * - use "s? blah blah" to use the "s" search engine for searching
 */

const { spawn } = require("child_process");

const staticEntries = {
    Localhost: [
        80,
        443,
        3000,
        3001,
        4000,
        4040,
        8080,
        8081,
    ],
    Gmail: "https://gmail.com",
    Drive: "https://drive.google.com",
    Keep: "https://keep.google.com",
    Photos: "https://photos.google.com",
    Calendar: "https://calendar.google.com",
    GitHub: "https://github.com",
    BitBucket: "https://bitbucket.org",
    DockerHub: "https://hub.docker.com",
    Reddit: "https://reddit.com",
    Hastebin: "https://hastebin.com",
    YouTube: "https://youtube.com",
    Netflix: "https://www.netflix.com",
    Sheets: "https://sheets.google.com",
    Twitter: "https://twitter.com",
    WakaTime: "https://wakatime.com",
};

const uriRegexes = [
    "^https?:/+",
    "^file:/+",
    // ssh?
    // mailto?
    // s?ftp?
]

const ipv4AddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
// const ipv6AddressRegex = ""; //todo.. maybe..
const hostnameRegex = "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$";

// spawn rofi child
const rofi = spawn("/usr/bin/rofi", ["-dmenu", "-i", "-p", "xdg-open"], {
    stdio: ["pipe", "pipe", null]
});
rofi.stdin.setDefaultEncoding("utf-8");

// write staticEntries to rofi's stdin
for (let prop in staticEntries) {
    rofi.stdin.write(prop + "\n");
}
rofi.stdin.end();

/**
 * Attempt to parse input using a stream. If I paste in a couple paragraphs
 * worth of input, this should probably Google the whole paragraph(s) as a
 * string.
 */
let inputData = [];
rofi.stdout.on("data", (data) => {
    inputData.push(data);
});
rofi.stdout.on("end", () => {
    let _inputString = inputData.toString().trim();

    // remove leading dots
    _inputString = _inputString.replace(/^\.+/g, "");
    // remove trailing dots
    _inputString = _inputString.replace(/\.+$/g, "");

    const inputString = _inputString;

    let launched = false;

    // the input will be zero-length if escape was pressed. exit in this case.
    if (inputString.length === 0) {
        console.log(`${process.argv0}: Detected user cancel. Bailing out.`);
        return 0;
    }

    // is the selected item in the list of staticEntries?
    if (staticEntries.hasOwnProperty(inputString)) {
        console.log(`${process.argv0}: Static entry "${inputString}" selected.`);

        // was it the localhost option?
        if (inputString === "Localhost") {
            // let the outer-scope know that we'll call launch() from here
            launched = true;

            // build a new rofi sub-menu
            const subRofi = spawn("/usr/bin/rofi", ["-dmenu", "-i", "-p", "Port"], {
                stdio: ["pipe", "pipe", null]
            });
            rofi.stdin.setDefaultEncoding("utf-8");

            // give the new client our list of common ports
            staticEntries[inputString].forEach((port) => {
                subRofi.stdin.write(port + "\n");
            });
            subRofi.stdin.end();

            // wait for an answer (no stream this time; max of 5 character input)
            subRofi.stdout.on("data", (data) => {
                const port = data.toString().trim();
                launch("http://localhost:" + port);
            });
        }
        if (!launched)
            return launched = launch(staticEntries[inputString]);
    }

    // is the input an exact URI?
    uriRegexes.forEach((regex) => {
        if (inputString.match(regex)) {
            console.log(`${process.argv0}: Exact URI detected.`);
            return launched = launch(inputString);
        }
    });

    // is the input a valid hostname or IP address?
    if (  (inputString.split(" ").length === 1)     // is it only 1 word?
       && (inputString.indexOf(".") !== -1)         // does it have at least one dot?
       && (inputString.match(ipv4AddressRegex) || inputString.match(hostnameRegex))
       )  {
            console.log(`${process.argv0}: ${inputString} matched host but not uri`);
            return launched = launch(`https://${inputString}`); // TODO: nslookup? simple 443/80 portscan?
    }

    // unmatched so far; google it \.:)./
    if (!launched) {
        return launch(`https://www.google.com/search?q=${inputString.replace(/\ /g, "+")}`);
    }
});

/**
 * Spawn a new instance of `xdg-open $url` in the background
 * @param {String} url to which to browse.
 * @returns {Number} child PID. null on failure.
 */
function launch(url) {
    console.log(`${process.argv0}: launch(): going to '${url}'`);
    const ff = spawn("xdg-open", [url], {
        stdio: "ignore",
        detached: true,
    });
    ff.unref();
    return 1;
}
