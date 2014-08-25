# 目录结构

所有文件都在一个`/data`， 例如 `/data`

* 源文件都存放在 `/data/src` 下
* log文件都存放在 `/data/logs`下

每一个项目都有一个`root_dir`

* 所有该项目的源文件都在 `/data/src/<root_dir>`下
* 所有该项目的logs文件都在 `/data/logs/<root_dir>`下


# 服务类型

服务类型包括：

1. nginx
2. php-fpm
3. php-cli
4. gearman
5. redis
6. mysql

# start agent server
```
python rest_server.py runserver
```

这个server会给matherload提供host的docker的信息， 并且提供控制container的接口