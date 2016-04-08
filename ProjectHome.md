# @itianqi 天气预报机器人用法 #
  * 订阅/退订/查询 天气预报订阅
    * 订阅：**@itianqi set 城市名** 或 **@itianqi set 城市全拼**
    * 退订：**@itianqi unset 城市名** 或 **@itianqi unset 城市全拼**
    * 查询：**@itianqi get**

> 天气预报将于每日早7时 和 晚6时 以reply形式推送. 并支持同时订阅多个城市的天气预报信息

  * **@itianqi tq 城市名** 或 **@itianqi tq 城市全拼**

> 获得最新实况天气信息(数据来自www.weather.com.cn)。如:
> _@tianqi 北京_ 或 _@itianqi beijing_

> ### 使用iPhone等终端可以看到天气图标 ###

> 今天是2011年1月8日,星期六,农历腊月初五

> 北京今日多云转晴 1度至-8度

> 08:40实况 -0.3度 西北风<3级 湿度22% (08:56:46)

> 未来两天天气状况:

> 明天 晴 -1度至-10度,

> 后天 晴 0度至-8度 (08:56:46)

  * **@itianqi time 城市**
> > 返回该城市当前时间
> > _@itianqi time Mountain View_
> > 当前时间: 2:38pm Thursday (PST), Mountain View, CA

  * **@itianqi jnr 纪念日** 或 **@itianqi jnr 纪念日 天数**


> 根据当前日期，以及明年的纪念日获得纪念日信息。 如

> _@itianqi jnr 2010-01-01 100_

> 第100天纪念日是2010-04-11, 您已经错过了272天!!

> @itianqi jnr 2010-01-01

> 今天是第371天纪念日, 距离下一个纪念日还有358天, 请做好准备!!

  * **@itianqi nl 公历日期**

> 公历农历转换，日期请采用 1985-09-06 或者 1985/09/06的形式


  * **@itianqi 农历** 或 **@itianqi 日期**

> 获得当前日期信息，如：

> _@itianqi 农历_

> 今天是2011年1月8日, 农历腊月初五 (08:19:25)

## Heading2 ##

即将加入的功能:

  * 世界时间











---


  1. emacs-config: emacs configuration files of my own
  1. chinese-convert: rename file/directory names from Traditional Chinese into Simplified Chiense, and the opposite. Thank [langconv](http://code.google.com/p/pyswim/)
> > For example, 学习=>學習 or 學習=>学习
  1. tweather: weather report for twitter.
  1. gpa\_calculator: gpa calculator
  1. check\_lcc: a load-cycle-count monitoring script for linux, plz refer [here](http://linuxtoy.org/archives/ubuntu-harddisk.html) for details
  1. rt\_vpn: guide traffic related to chinese ip to use your former gateway other than vpn server