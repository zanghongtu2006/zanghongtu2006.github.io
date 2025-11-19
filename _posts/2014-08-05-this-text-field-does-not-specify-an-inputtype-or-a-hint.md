---
title: "This text field does not specify an inputType or a hint"
date: "2014-08-05 17:39:17"
slug: "this-text-field-does-not-specify-an-inputtype-or-a-hint"
layout: "post"
categories: ["Android"]
tags: ["This text field does not specify an inputType or a hint", "Android"]
---
android开发过程中突然发现的warning

EditText 报出 “This text field does not specify an inputType ora hint”

原因：

EditText需要指定默认输入类型

加入android:inputType="number|phone"，表示指定为数字或电话

inputtype类型如下：

//文本类型，多为大写、小写和数字符号。  
    android:inputType="none"  
    android:inputType="text"  
    android:inputType="textCapCharacters"  
    android:inputType="textCapWords"  
    android:inputType="textCapSentences"  
    android:inputType="textAutoCorrect"  
    android:inputType="textAutoComplete"  
    android:inputType="textMultiLine"  
    android:inputType="textImeMultiLine"  
    android:inputType="textNoSuggestions"  
    android:inputType="textUri"  
    android:inputType="textEmailAddress"  
    android:inputType="textEmailSubject"  
    android:inputType="textShortMessage"  
    android:inputType="textLongMessage"  
    android:inputType="textPersonName"  
    android:inputType="textPostalAddress"  
    android:inputType="textPassword"  
    android:inputType="textVisiblePassword"  
    android:inputType="textWebEditText"  
    android:inputType="textFilter"  
    android:inputType="textPhonetic"  
//数值类型  
    android:inputType="number"  
    android:inputType="numberSigned"  
    android:inputType="numberDecimal"  
    android:inputType="phone"//拨号键盘  
    android:inputType="datetime"  
    android:inputType="date"//日期键盘  
    android:inputType="time"//时间键盘
