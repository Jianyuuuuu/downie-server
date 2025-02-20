# 自定义集成

Downie的自定义集成是一个强大的功能，它允许你为不支持的网站添加自定义处理程序。在Downie v4.7之前，这需要一些JavaScript知识，因为它是在网页上下文中使用的。但从Downie v4.7开始，你可以在不编写任何代码的情况下添加网站支持（需要macOS 14.0或更高版本）。

## 1. 定义URL正则表达式

添加集成时，首先需要为该集成处理的链接定义正则表达式。例如，如果你想支持类似`https://www.youtube.com/watch?v=MzPECgrwjKE`这样的链接，你可以使用类似`https?://www\.youtube\.com/watch\?v=[\w_-]+`的正则表达式。关于正则表达式的更多信息，请参见https://en.wikipedia.org/wiki/Regular_expression，网上还有许多其他资源。

可选地，你可以在正则表达式中使用名为`ID`的命名组来定义标识符。当Downie从未知来源提取链接时，标识符有助于查找重复结果。标识符不能为空，并且应该唯一标识它所指向的内容。在上面的YouTube示例中，视频ID就是v查询参数的值。要添加命名组，请使用`(?P<ID>id_regex)`将ID部分包围起来 - 即`https?://www\.youtube\.com/watch\?v=(?P<ID>[\w_-]+)`。有关命名正则表达式组的更多信息，请搜索相关资料。

## 2. 执行类型

一旦设置了正则表达式过滤器，有两个选项 - 运行JavaScript或运行资源检测。每种方式都有其优势和劣势。

### JavaScript

#### 优势
- JavaScript更强大，你可以做任何你想做的事
- 你可以加载外部资源
- 你可以为Downie提供元数据、字幕等
- 它确实是一个完全独立的集成，就像Downie内置的那些一样（尽管Downie原生运行代码并用Swift编写，但代码做类似的事情）

#### 劣势
- 你需要有一些编程知识
- 你需要深入网站寻找资源，这可能会让许多用户感到困扰

### 资源检测

#### 优势
- 配置超级简单 - 只需让Downie知道要匹配哪个资源
- 如果你不熟悉用户引导提取，请尝试使用它 - 它基本上是在自动化这个功能 - 你会得到相同的结果

#### 劣势
- 目前，你只能匹配一个资源，成功匹配后Downie就会停止评估 - 即你无法提取播放列表等
- 你无法调整标题或元数据提取
- 如果字幕不是结果的一部分（例如HLS流），则无法分配它们
- 你无法指定单独的视频和音频部分
- 对下载的微调选项有限（例如指定HTTP头）

## 3. 实现选项

### 选项A - 资源检测

使用资源检测时，只有几个选项：

- **匹配范围** - 允许匹配完整URL或仅最后的路径组件
  - 示例：`https://www.example.com/test/foo/bar/master.m3u8?sign=43843u990348398`是完整URL
  - `master.m3u8`是最后的路径组件

- **匹配类型** - 允许字面匹配（不区分大小写）或正则表达式匹配
  - 匹配不是完全匹配（除非你使用带有`^`前缀和`$`后缀的正则表达式）
  - `master.m3u8`也会匹配`video_master.m3u8`和`audio_master.m3u8`
  - 如果你需要消除这样的问题，可以使用完整URL匹配并使用`/master.m3u8`，或使用正则表达式选项并定义开始（`^`）和结束（`$`）

- **匹配** - 实际的匹配内容 - 根据匹配类型，它被解释为正则表达式或字面值

**注意：**如果网站使用例如YouTube或Vimeo嵌入文件，你可以匹配该链接。Downie会识别这一点，并使用内置集成提取实际下载。

### 选项B - JavaScript

设置URL正则表达式后，你需要定义JavaScript代码。代码在网页视图组件加载网页后加载 - 类似于在Safari的Web检查器控制台中编写内容。你在这里做什么完全取决于你。

与Downie通信有3种方法：

#### 1. 报告直接下载

使用`window.downie.reportDownload(download)`向Downie报告你找到了直接下载。直接下载是直接指向文件（例如MP4）的链接 - 与嵌入内容（例如YouTube链接）不同。

下载必须是具有以下字段的字典对象：

- `url` - 这是唯一必需的字段，必须是有效的URL。这是你想要Downie下载的链接。从Downie v4.3开始，这已被弃用，改用qualities
- `qualities` - 下载数组 - 见下文更多信息
- `subtitles` - 可选，字幕数组
- `title` - 下载名称
- `description` - 可选，描述
- `preview` - 预览图片URL
- `playlistName` - 你可以包含播放列表名称
- `playlistIndex` - 播放列表中的索引。索引从1开始（不是从零开始）
- `playlistCount` - 如果你知道播放列表中的下载数量，这就是数量
- `showName` - 节目名称
- `authors` - 作者列表（字符串数组）

##### 质量

`qualities`字段应该是一个字典数组，定义网站提供的不同质量。最低要求的字段是`url`，它定义了下载的URL。其他可选允许的字段是：

- `width` - 定义此版本的宽度的整数
- `height` - 定义此版本的高度的整数
- `headers` - 键值对字典，定义下载时应使用的HTTP头
- `encryptionKeyHeaderFields` - 键值对字典，定义加载HLS流中的加密密钥时应使用的HTTP头
- `disableChunkedDownloads` - 如果设置为true，则Downie将把下载视为禁用了分块下载
- `audioQuality` - 如果版本由单独的音频和视频流组成（需要Downie v4.5.2或更高版本）

示例：

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

##### 字幕

如果填充了下载对象的`subtitles`字段，它必须包含一个字典数组，每个字典必须包含这两个字段：

- `url` - 字幕文件的URL
- `title` - 字幕的标题 - 例如语言。如果没有特定标题，输入"subtitles"或类似内容

示例：

```javascript
download.subtitles = [
    {
        "url": "https://www.example.com/subtitles.srt",
        "title": "en"
    }
]
```

#### 2. 报告嵌入下载

使用`window.downie.reportEmbeddedDownload(download)`向Downie报告你找到了嵌入下载，例如YouTube或Vimeo链接。

下载必须是具有以下字段的字典对象：

- `url` - 这是唯一必需的字段，必须是有效的URL
- `title` - 如果你想覆盖标题，则为下载名称
- `playlistName` - 你可以包含播放列表名称
- `playlistIndex` - 播放列表中的索引（从1开始）
- `playlistCount` - 如果你知道播放列表中的下载数量
- `showName` - 节目名称
- `authors` - 作者列表（字符串数组）
- `context` - 可选，你可以将上下文传递给嵌入下载器

#### 3. 报告完成

这很重要 - 添加完下载后，你应该调用`window.downie.reportDone();`。这告诉Downie你已完成，它将处理你报告的下载。如果你不这样做，Downie将等待60秒的默认超时时间才处理结果。

#### 4. 报告错误

使用`window.downie.reportError("出错了。")`向Downie报告脚本未找到你要找的内容。这会导致Downie关闭网页视图并在UI中显示错误。

#### 5. 日志记录

使用`window.downie.log("某些内容")`让Downie在调试日志中记录内容。要启用调试日志，请参见菜单栏中的Debug菜单。

#### 6. 使用上下文

从Downie v4.6.1开始，`window.downie`对象将包含一个`context`字段。这将是一个可能包含`referer`字段（包含引用URL）的字典。

在集成之间传递信息的示例：

```javascript
// 播放列表：
for (...) {
    var download = { ... };
    download.context = {
        "playlist": "某个播放列表",
        "index": 200,
        "count": 400
    };
    downie.reportEmbeddedDownload(download);
}

// 单个视频：
var playlistName = downie.context.playlist;
// ...
```

## 测试

你可以在首选项 > 自定义集成中打开控制台窗口并查看记录的内容。注意，如果下载失败，你应该从队列中删除下载，并在修改源代码后再次添加它。重试队列中已有的下载将运行原始代码。

## 实际示例

这是一个简单的实际示例（这个示例实际上可以在很多网站上使用）。更多示例可以在自定义集成的GitHub仓库中找到。

示例URL：`http://www-db.deis.unibo.it/courses/TW/DOCS/w3schools/html/html5_video.asp.html`
集成正则表达式：`https?://[^/]*unibo\.it/courses/.*/html/.*`

这个网页使用HTML `<video>`标签和内部的`<source>`标签，所以你使用`document.getElementsByTagName`定位它们并提取URL：

```javascript
function getDownload() {
    var elements = document.getElementsByTagName("source");
    if (elements.length == 0) {
        // 未找到<source>标签。
        window.downie.reportError("没有视频元素。");
        return null;
    }    

    var url = elements[0].src;
    if (url == null || url == "") {
        // source值未加载，或不存在。
        window.downie.reportError("视频元素中没有视频URL。");
        return null;
    }    

    var download = {
        "qualities": [
            {
                "url": url
            }
        ],
        "title": "示例下载",
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