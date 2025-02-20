# Custom Integrations

Custom integrations are a powerful feature in Downie that allows you to add custom handlers for sites that are not supported. Until Downie v4.7, it required some knowledge of JavaScript which is used in context of the webpage, but starting with Downie v4.7, you can add support for sites without writing a single line of code (requires macOS 14.0 or later).

## 1. Defining URL Regex

When you add an integration, first you need to define regex for links that are handled by this integration. For example, if you for want to support links such as `https://www.youtube.com/watch?v=MzPECgrwjKE`, you would use a regex similar to `https?://www\.youtube\.com/watch\?v=[\w_-]+`. For more information about regex, please see e.g. https://en.wikipedia.org/wiki/Regular_expression but there are many other resources online.

Optionally, you can define an identifier within the regex using a named group called `ID`. Identifiers help Downie when looking for duplicate results in case it is extracting links from an unknown source. The identifier must not be empty and should uniquely identify the content it points to. In case of the YouTube example above, it's the video ID that is the v query parameter value. To add the named group, surround the ID part with `(?P<ID>id_regex)` - i.e. `https?://www\.youtube\.com/watch\?v=(?P<ID>[\w_-]+)`. Google for named regex groups for more information.

## 2. Execution Type

Once you have a regex filter in place, there are two options - either run JavaScript, or run Resource Detection. Each has its own advantages and disadvantages.

### JavaScript

#### Advantages
- JavaScript is more powerful in a sense that you can do whatever you want
- You can load external resources
- You can provide Downie with metadata, subtitles, etc.
- It is indeed a fully standalone integration like the ones that are part of Downie (though Downie runs the code natively and is written in Swift, the code does something similar)

#### Disadvantages
- You need to have some programming knowledge
- You need to dig through the site to find the resources which can be discouraging to many users

### Resource Detection

#### Advantages
- It is super easy to configure - just let Downie know which resource to match
- If you are not familiar with the User-Guided Extraction, please try the link with it - it's pretty much automating this feature - you get the same results

#### Disadvantages
- Currently, you can only match one resource, after a successful match, Downie stops the evaluation - i.e. you cannot extract e.g. a playlist
- You cannot adjust the title or metadata extraction
- If the subtitles are not part of the result (e.g. HLS Stream), then they cannot be assigned
- You cannot specify separate video and audio parts
- There are limited options for fine-tuning the downloads (e.g. specifying HTTP headers)

## 3. Implementation Options

### Option A - Resource Detection

When using resource detection, there's just a few options:

- **match scope** - this allows matching either the full URL or just the last path component
  - Example: `https://www.example.com/test/foo/bar/master.m3u8?sign=43843u990348398` is the full URL
  - `master.m3u8` is the last path component

- **match type** - this allows either literal match (case insensitive) or a regex match
  - The match is not a full match (unless you use regex with `^` prefix and `$` suffix)
  - `master.m3u8` will also match `video_master.m3u8` and `audio_master.m3u8`
  - If you need to eliminate issues like this, use either a full URL match and use `/master.m3u8`, or use regex option and define start (`^`) and end (`$`)

- **match** - the actual match - it is either interpreted as regex or a literal, depending on the match type

**Note:** If the site uses e.g. YouTube or Vimeo embed files, you can match that link. Downie will recognize this and will extract the actual downloads using the built-in integration.

### Option B - JavaScript

After setting up the URL regex, you need to define the JavaScript code. The code is loaded after a web view component loads the webpage - similar to when you write something into a console in the web inspector in Safari. What you do here is completely up to you.

For communicating with Downie, there are 3 methods:

#### 1. Reporting a direct download

Use `window.downie.reportDownload(download)` to report to Downie that you've found a direct download. Direct download is a link that leads directly to a file (e.g. MP4) - unlike embedded content which would be e.g. a YouTube link.

The download must be a dictionary object with the following fields:

- `url` - this is the only required field and must be a valid URL. It is the link you want Downie to download. Starting Downie v4.3, this is deprecated in favor of qualities
- `qualities` - an array of downloads - see below for more information
- `subtitles` - optionally, an array of subtitles
- `title` - name of the download
- `description` - optionally, description
- `preview` - image preview URL
- `playlistName` - you can include playlist name
- `playlistIndex` - index within the playlist. The index starts at 1 (it's not zero-based)
- `playlistCount` - if you know the number of downloads in the playlist, this is the number
- `showName` - name of the show
- `authors` - list of authors (an array of strings)

##### Qualities

The field `qualities` should be an array of dictionaries defining different qualities provided by the site. The minimum required field is `url` which defines the URL to the download. Additional optional allowed fields are:

- `width` - integer defining the width of this rendition
- `height` - integer defining the height of this rendition
- `headers` - a dictionary of key-value pairs that define HTTP headers that should be used for the download
- `encryptionKeyHeaderFields` - a dictionary of key-value pairs that define HTTP headers that should be used for loading encryption key in HLS streams
- `disableChunkedDownloads` - if set to true, then Downie will treat the download as if chunked downloads were disabled
- `audioQuality` - if the rendition consists of separate audio and video streams (requires Downie v4.5.2 or later)

Example:

```javascript
var download = {
    "qualities": [
        {
            "url": "https://www.example.com/file.mp4",
            "width": 1024,
            "height": 768,
            "headers": {
                "Referer": "https://www.example.com"
            }
        }
    ]
};

window.downie.reportDownload(download);
window.downie.reportDone();
```

##### Subtitles

The field `subtitles` of the download object, if populated, must contain an array of dictionaries and each dictionary must contain these two fields:

- `url` - URL of the subtitles file
- `title` - title of the subtitles - e.g. language. If there is no specific title, enter "subtitles" or something like that

Example:

```javascript
download.subtitles = [
    {
        "url": "https://www.example.com/subtitles.srt",
        "title": "en"
    }
]
```

#### 2. Reporting an embedded download

Use `window.downie.reportEmbeddedDownload(download)` to report to Downie that you've found an embedded download, e.g. a YouTube or Vimeo link.

The download must be a dictionary object with the following fields:

- `url` - this is the only required field and must be a valid URL
- `title` - name of the download in case you want to override the title
- `playlistName` - you can include playlist name
- `playlistIndex` - index within the playlist (starts at 1)
- `playlistCount` - if you know the number of downloads in the playlist
- `showName` - name of the show
- `authors` - list of authors (an array of strings)
- `context` - optionally, you can pass a context to the embedded downloader

#### 3. Reporting you are done

This is very important - after you are done adding downloads, you should call `window.downie.reportDone();`. This tells Downie that you are done and it will process the downloads that you've reported. If you don't do this, Downie will wait for a default timeout of 60 seconds before processing the results.

#### 4. Reporting an error

Use `window.downie.reportError("Something went wrong.")` to report to Downie that the script failed to find what you were looking for. This causes Downie to close the web view and display the error in the UI.

#### 5. Logging

Use `window.downie.log("Something")` to have Downie log something into the debug log. To enable the debug log, see the Debug menu in the menu bar.

#### 6. Using Context

Since Downie v4.6.1, the `window.downie` object will contain a field `context`. This will be a dictionary that may contain the `referer` field (which contains the referring URL).

Example of passing information between integrations:

```javascript
// Playlist:
for (...) {
    var download = { ... };
    download.context = {
        "playlist": "Some Playlist",
        "index": 200,
        "count": 400
    };
    downie.reportEmbeddedDownload(download);
}

// Individual video:
var playlistName = downie.context.playlist;
// ...
```

## Testing

You can open a Console window in Preferences > Custom Integrations and see the logged content. Note that if the download fails, you should remove the download from the queue and add it again after modifying the source code. Retrying a download that's already in the queue will run the original code.

## Real-World Example

Here is a simple real-world example (and this example is actually usable on quite a few sites). More examples can be found in the GitHub repo for custom integrations.

Example URL: `http://www-db.deis.unibo.it/courses/TW/DOCS/w3schools/html/html5_video.asp.html`
Integration Regex: `https?://[^/]*unibo\.it/courses/.*/html/.*`

This webpage uses HTML `<video>` tags and `<source>` tags inside, so you locate them using `document.getElementsByTagName` and extract the URL:

```javascript
function getDownload() {
    var elements = document.getElementsByTagName("source");
    if (elements.length == 0) {
        // No <source> tags found.
        window.downie.reportError("No video elements.");
        return null;
    }    

    var url = elements[0].src;
    if (url == null || url == "") {
        // The source value is not loaded, or doesn't exist.
        window.downie.reportError("No video URL in video element.");
        return null;
    }    

    var download = {
        "qualities": [
            {
                "url": url
            }
        ],
        "title": "Example Download",
        "preview": elements[0].parentElement.poster
    };
    return download;
}

var download = getDownload();
if (download != null) {
    window.downie.reportDownload(download);
    window.downie.reportDone();
}
```