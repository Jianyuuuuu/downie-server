# Downie Automation Guide

Downie can be used in various automated workflows as well. This help topic will cover this.

## Automated Mode

From time to time, Downie needs to show you some kind of a prompt (login dialog, subtitle selection, etc.). If you are away from the machine, this can be unwanted as it blocks the UI and processing of the links in the background. For this, there is the "automated mode" which can be enabled in Settings > Advanced. When run in automated mode, Downie will suppress all dialogs. Please keep in mind that this has its risks - e.g. if Downie requires you to login, it will cancel the attempt automatically and the download will fail.

## Opening Links in Downie

The main question now is how to open a link in Downie. There are several options.

### Open a link with no options

If you just need to open a link in Downie, then it's simple - if you are using a shell (command line), use the open command:

```bash
open -a 'Downie 4' 'https://www.example.com/'
```

Several notes:

- If you are running a Setapp version, use Downie instead of Downie 4
- `&` is a shell operator. Make sure that the link is surrounded by single or double quotes.

If you are using Apple Script, use the open command:

```applescript
tell application "Downie 4"
    open location "https://www.example.com/"
end tell
```

In Automator, you can use the Open URLs in Downie Automator action.

### Open a link with options

Sometimes, you want some links to be opened with particular postprocessing, or even in the User-Guided Extraction. For this, Downie uses a custom scheme `downie://`. Here is an example:

```
downie://XUOpenURL?url=https://www.example.com/&postprocessing=audio
```

Let's break this down. The first part `downie://XUOpenURL` is fixed. After that, there is the query separator (`?`) and regular URL query parameters. In URLs, query parameters are separated by `&` and are in format `name=value`. In this case, there are two parameters - `url` (whose value is `https://www.example.com/`) and `postprocessing` whose value is `audio`.

### Supported Parameters

There are several supported parameters:

#### url (required)
This is the actual link you want to open. Please make sure that the link is URL-encoded. This mainly means that all `&` characters within the link must be encoded.

Example: if the link is `https://www.youtube.com/watch?v=eSc2gwNrc8M&ab_channel=VisualGolf` - you can notice that the link itself contains `?` and `&`. If you pasted the link into the Downie custom link just as-is, you'd get:

❌ **Incorrect:**
```
downie://XUOpenURL?url=https://www.youtube.com/watch?v=eSc2gwNrc8M&ab_channel=VisualGolf&postprocessing=audio
```
This is wrong as it will be interpreted incorrectly - the `ab_channel` parameter will not be interpreted as part of the url.

✅ **Correct:**
```
downie://XUOpenURL?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DeSc2gwNrc8M%26ab_channel%3DVisualGolf&postprocessing=audio
```

To make it super easy for you, make sure that you replace:
- `?` with `%3F`
- `&` with `%26`

#### postprocessing (optional)
Set a certain postprocessing. Allowed values are:
- `mp4` - MP4 postprocessing
- `audio` - extract audio only
- `permute` - send to Permute

#### destination (optional)
Path to destination folder. Make sure that the folder exists.

#### action (optional)
Perform certain action. Currently there's only one action:
- `open_in_uge` - opens the link in the User-Guided Extraction. Ignores the postprocessing argument.

### Using Custom Links

Once you have this custom link, the workflow is the same - either use the shell command:
```bash
open -a 'Downie 4' 'downie://...'
```

Or use the same with Apple Script.