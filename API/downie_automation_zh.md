# Downie 自动化指南

Downie 可以用于各种自动化工作流程。本指南将为您介绍相关内容。

## 自动化模式

有时候，Downie 需要向您显示某些提示（如登录对话框、字幕选择等）。如果您不在电脑旁边，这可能会造成不便，因为它会阻塞界面和后台链接的处理。为此，Downie 提供了"自动化模式"，可以在 设置 > 高级 中启用。在自动化模式下，Downie 将抑制所有对话框。请注意，这样做有一定风险 - 例如，如果 Downie 需要您登录，它会自动取消尝试，下载将会失败。

## 在 Downie 中打开链接

现在的主要问题是如何在 Downie 中打开链接。这里有几种方式。

### 无选项打开链接

如果您只需要在 Downie 中打开一个链接，那很简单 - 如果您使用 shell（命令行），请使用 open 命令：

```bash
open -a 'Downie 4' 'https://www.example.com/'
```

几点注意事项：

- 如果您使用的是 Setapp 版本，请使用 Downie 而不是 Downie 4
- `&` 是 shell 运算符。确保链接用单引号或双引号括起来。

如果您使用 Apple Script，请使用 open 命令：

```applescript
tell application "Downie 4"
    open location "https://www.example.com/"
end tell
```

在 Automator 中，您可以使用 Open URLs in Downie 自动化操作。

### 带选项打开链接

有时，您可能希望某些链接以特定的后处理方式打开，或者在用户引导提取中打开。为此，Downie 使用自定义方案 `downie://`。这里是一个例子：

```
downie://XUOpenURL?url=https://www.example.com/&postprocessing=audio
```

让我们来分析一下。第一部分 `downie://XUOpenURL` 是固定的。之后是查询分隔符（`?`）和常规 URL 查询参数。在 URL 中，查询参数用 `&` 分隔，格式为 `name=value`。在这个例子中，有两个参数 - `url`（其值为 `https://www.example.com/`）和 `postprocessing`（其值为 `audio`）。

### 支持的参数

以下是几个支持的参数：

#### url（必需）
这是您想要打开的实际链接。请确保链接进行了 URL 编码。这主要意味着链接中的所有 `&` 字符都必须编码。

例如：如果链接是 `https://www.youtube.com/watch?v=eSc2gwNrc8M&ab_channel=VisualGolf` - 您可以注意到链接本身包含 `?` 和 `&`。如果您直接将链接粘贴到 Downie 自定义链接中，会得到：

❌ **错误：**
```
downie://XUOpenURL?url=https://www.youtube.com/watch?v=eSc2gwNrc8M&ab_channel=VisualGolf&postprocessing=audio
```
这是错误的，因为它会被错误解释 - `ab_channel` 参数不会被解释为 url 的一部分。

✅ **正确：**
```
downie://XUOpenURL?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DeSc2gwNrc8M%26ab_channel%3DVisualGolf&postprocessing=audio
```

为了让操作更简单，请确保替换：
- `?` 替换为 `%3F`
- `&` 替换为 `%26`

#### postprocessing（可选）
设置特定的后处理。允许的值有：
- `mp4` - MP4 后处理
- `audio` - 仅提取音频
- `permute` - 发送到 Permute

#### destination（可选）
目标文件夹路径。请确保该文件夹存在。

#### action（可选）
执行特定操作。目前只有一个操作：
- `open_in_uge` - 在用户引导提取中打开链接。忽略 postprocessing 参数。

### 使用自定义链接

一旦您有了这个自定义链接，工作流程是相同的 - 可以使用 shell 命令：
```bash
open -a 'Downie 4' 'downie://...'
```

或者使用相同的 Apple Script。