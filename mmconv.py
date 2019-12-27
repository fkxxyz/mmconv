#!/bin/python3

import os
import gettext
import random
import base64
import zipfile
import sys
import time
import datetime
import argparse
import json
import uuid
import xml.dom.minidom


# 为了方便单文件便携，在这里支持中文和英文
if gettext.locale.getlocale()[0].startswith('zh'):
    msg_not_a_valid_file = '不是一个有效的 %s 文件。'
    msg_has_no = '缺少 %s 。'
    msg_error_format_in = '错误的格式： %s 。'
    msg_document = '文档'
    msg_write_failed_file = '写入失败： %s 。'
    msg_load_failed_file = '读取失败： %s 。'
    msg_no_such_file = '没有这样的文件： %s 。'
    msg_is_directory = '忽略文件夹： %s 。'

    msg_argument_description = "思维导图文档转换器，项目地址： https://github.com/fkxxyz/mmconv"
    msg_arg_src = '源文件。表示要转换的文件。'
    msg_arg_dest = '目标文件名。转换成功的保存的文件路径。如果未指定目标文件，则直接打印源文件类型。'
    msg_arg_type = '指定目标文件的类型。目前支持以下类型：'

else:
    msg_not_a_valid_file = 'Not a valid %s file. '
    msg_has_no = 'Has no %s . '
    msg_error_format_in = 'Error format in %s . '
    msg_document = 'document'
    msg_write_failed_file = 'Write failed: %s .'
    msg_load_failed_file = 'Load failed: %s .'
    msg_no_such_file = 'No such file: %s .'
    msg_is_directory = 'Is directory: %s .'

    msg_argument_description = "Mind map document converter. Project address https://github.com/fkxxyz/mmconv"
    msg_arg_src = 'source file. The file to be converted.'
    msg_arg_dest = 'destination file. Path of the saved file that was successfully converted. If no destination file is specified, the source file type is printed.'
    msg_arg_type = 'specify the type of destination file. Support for these document types: '


def mindjet_Document_xml_head_func(generateMapID):
    return b'''<?xml version="1.0" encoding="UTF-8"?><ap:Map xmlns:ap="http://schemas.mindjet.com/MindManager/Application/2003" xmlns:cor="http://schemas.mindjet.com/MindManager/Core/2003" xmlns:pri="http://schemas.mindjet.com/MindManager/Primitive/2003" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Dirty="0000000000000001" Gen="0000000000000000" OId="''' + generateMapID() + b'''" xsi:schemaLocation="http://schemas.mindjet.com/MindManager/Application/2003 http://schemas.mindjet.com/Min">
<cor:Custom xmlns:cst0="http://schemas.mindjet.com/MindManager/UpdateCompatibility/2004" Dirty="0000000000000000" Index="0" Uri="http://schemas.mindjet.com/MindManager/UpdateCompatibility/2004" cst0:UpdatedCategories="true" cst0:UpdatedVisibilityStyle="true"/>
<ap:OneTopic>
'''

mindjet_Document_xml_text_tail = b'''
</ap:OneTopic>
<ap:Relationships/>
<ap:StyleGroup>
<ap:RootTopicDefaultsGroup>
<ap:DefaultColor Dirty="0000000000000000" FillColor="ff96b3df" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Central Topic" ReadOnly="false" TextAlignment="urn:mindjet:Center" TextCapitalization="urn:mindjet:SentenceStyle" VerticalTextAlignment="urn:mindjet:Top">
<ap:Font Bold="true" Color="ff333333" Italic="false" Name="Verdana" Size="12." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="2.5" Dirty="0000000000000000" LeftMargin="2.5" RightMargin="2.5" SubTopicShape="urn:mindjet:RoundedRectangle" TopMargin="2.5" VerticalBottomMargin="2.5" VerticalLeftMargin="2.5" VerticalRightMargin="2.5" VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="2.5"/>
<ap:DefaultLabelFloatingTopicShape BottomMargin="0." Dirty="0000000000000000" LabelFloatingTopicShape="urn:mindjet:None" LeftMargin="0." RightMargin="0." TopMargin="0." VerticalBottomMargin="2.5" VerticalLabelFloatingTopicShape="urn:mindjet:None" VerticalLeftMargin="2.5" VerticalRightMargin="2.5" VerticalTopMargin="2.5"/>
<ap:DefaultCalloutFloatingTopicShape BottomMargin="0." CalloutFloatingTopicShape="urn:mindjet:None" Dirty="0000000000000000" LeftMargin="0." RightMargin="0." TopMargin="0." VerticalBottomMargin="2.5" VerticalCalloutFloatingTopicShape="urn:mindjet:None" VerticalLeftMargin="2.5" VerticalRightMargin="2.5" VerticalTopMargin="2.5"/>
<ap:DefaultTopicLayout Dirty="0000000000000000" MinimumHeight="5." Padding="2." TopicLayoutHorizontalAlignment="urn:mindjet:Center" TopicLayoutVerticalAlignment="urn:mindjet:Center" TopicTextAndImagePosition="urn:mindjet:TextRightImageLeft" TopicWidthControl="urn:mindjet:AutoWidth" Width="61."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="7." DistanceFromParent="30." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsConnectionPoint="urn:mindjet:Center" SubTopicsConnectionStyle="urn:mindjet:Arc" SubTopicsDepth="1" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:LeftAndRight" SubTopicsShape="urn:mindjet:Vertical" SubTopicsShapeWidthFactor="1." SubTopicsTreeConnectionPoint="urn:mindjet:Inside" SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:Down" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="10." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow" VerticalSubTopicsTreeConnectionPoint="urn:mindjet:Inside"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:RootTopicDefaultsGroup>
<ap:RootSubTopicDefaultsGroup Level="0">
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffe9f1ff" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Main Topic" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="true" Color="ff4b4b4b" Italic="false" Name="Verdana" Size="10." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="2." Dirty="0000000000000000" LeftMargin="2." RightMargin="2." SubTopicShape="urn:mindjet:RoundedRectangle" TopMargin="2." VerticalBottomMargin="2." VerticalLeftMargin="2." VerticalRightMargin="2." VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="2."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" Padding="2." Width="66.800003051757813"/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="2." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Bottom" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="10." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:RootSubTopicDefaultsGroup>
<ap:RootSubTopicDefaultsGroup Level="1">
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffffffff" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Subtopic" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="true" Color="ff4b4b4b" Italic="false" Name="Verdana" Size="9." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="0." Dirty="0000000000000000" LeftMargin="0." RightMargin="0." SubTopicShape="urn:mindjet:None" TopMargin="0." VerticalBottomMargin="1." VerticalLeftMargin="1." VerticalRightMargin="1." VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="1."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" Width="60.700000762939453"/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="2." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Bottom" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="10." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:RootSubTopicDefaultsGroup>
<ap:RootSubTopicDefaultsGroup Level="2">
<ap:DefaultColor Dirty="0000000000000000" FillColor="00000000"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Subtopic" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="false" Color="ff282828" Italic="false" Name="Verdana" Size="9." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="0.20000000298023224" Dirty="0000000000000000" LeftMargin="0.20000000298023224" RightMargin="0.20000000298023224" SubTopicShape="urn:mindjet:Line" TopMargin="0.20000000298023224" VerticalBottomMargin="1." VerticalLeftMargin="1." VerticalRightMargin="1." VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="1."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" Width="66.800003051757813"/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="2." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Bottom" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="10." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
</ap:RootSubTopicDefaultsGroup>
<ap:CalloutTopicDefaultsGroup>
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffffe178" LineColor="ffe0c35a"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Callout" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="true" Color="ff4b4b4b" Italic="false" Name="Verdana" Size="10." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultCalloutFloatingTopicShape BottomMargin="2." CalloutFloatingTopicShape="urn:mindjet:RoundedRectangleBalloon" Dirty="0000000000000000" LeftMargin="2." RightMargin="2." TopMargin="2."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" Padding="2." Width="61."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="2." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="10."/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:CalloutTopicDefaultsGroup>
<ap:CalloutSubTopicDefaultsGroup Level="0">
<ap:DefaultColor Dirty="0000000000000000" FillColor="00000000" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Subtopic" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="false" Color="ff282828" Name="Verdana" Size="9."/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="0.20000000298023224" Dirty="0000000000000000" LeftMargin="0.20000000298023224" RightMargin="0.20000000298023224" SubTopicShape="urn:mindjet:Line" TopMargin="0.20000000298023224"/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="2." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="10."/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:CalloutSubTopicDefaultsGroup>
<ap:LabelTopicDefaultsGroup>
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffeeeff6" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Floating Topic" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="true" Color="ff4b4b4b" Italic="false" Name="Verdana" Size="10." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultLabelFloatingTopicShape BottomMargin="2." Dirty="0000000000000000" LabelFloatingTopicShape="urn:mindjet:RoundedRectangle" LeftMargin="2." RightMargin="2." TopMargin="2." VerticalBottomMargin="2." VerticalLabelFloatingTopicShape="urn:mindjet:RoundedRectangle" VerticalLeftMargin="2." VerticalRightMargin="2." VerticalTopMargin="2."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" Padding="2."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="2." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsDepth="1" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:Down" VerticalDistanceBetweenSiblings="1.3999999761581421" VerticalDistanceFromParent="5." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:LabelTopicDefaultsGroup>
<ap:LabelSubTopicDefaultsGroup Level="0">
<ap:DefaultColor Dirty="0000000000000000" FillColor="00000000" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Subtopic" ReadOnly="false" TextAlignment="urn:mindjet:Left" TextCapitalization="urn:mindjet:None">
<ap:Font Bold="false" Color="ff282828" Name="Verdana" Size="9."/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="0.5" Dirty="0000000000000000" LeftMargin="0.5" RightMargin="0.5" SubTopicShape="urn:mindjet:Line" TopMargin="0.5" VerticalBottomMargin="1." VerticalLeftMargin="1." VerticalRightMargin="1." VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="1."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" Width="61."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Bottom" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:RoundedElbow" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1.3999999761581421" VerticalDistanceFromParent="3." VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:LabelSubTopicDefaultsGroup>
<ap:OrgChartTopicDefaultsGroup>
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffe9f1ff" LineColor="ffc6c6c6"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Org-Chart Topic" ReadOnly="false" TextAlignment="urn:mindjet:Center" TextCapitalization="urn:mindjet:None" VerticalTextAlignment="urn:mindjet:Top">
<ap:Font Bold="true" Color="ff4b4b4b" Italic="false" Name="Verdana" Size="10." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape Dirty="0000000000000000" VerticalBottomMargin="2." VerticalLeftMargin="2." VerticalRightMargin="2." VerticalSubTopicShape="urn:mindjet:RoundedRectangle" VerticalTopMargin="2."/>
<ap:DefaultLabelFloatingTopicShape Dirty="0000000000000000" VerticalBottomMargin="2." VerticalLabelFloatingTopicShape="urn:mindjet:RoundedRectangle" VerticalLeftMargin="2." VerticalRightMargin="2." VerticalTopMargin="2."/>
<ap:DefaultCalloutFloatingTopicShape Dirty="0000000000000000" VerticalBottomMargin="2." VerticalCalloutFloatingTopicShape="urn:mindjet:RoundedRectangleBalloon" VerticalLeftMargin="2." VerticalRightMargin="2." VerticalTopMargin="2."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" MinimumHeight="5." Padding="2." TopicLayoutHorizontalAlignment="urn:mindjet:Center" TopicLayoutVerticalAlignment="urn:mindjet:Center" TopicTextAndImagePosition="urn:mindjet:TextRightImageLeft" TopicWidthControl="urn:mindjet:AutoWidth" Width="50."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1." DistanceFromParent="5." SubTopicsAlignment="urn:mindjet:Center" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsDepth="1" SubTopicsGrowth="urn:mindjet:Vertical" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsShapeWidthFactor="1." SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1.3999999761581421" VerticalDistanceFromParent="3." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:OrgChartTopicDefaultsGroup>
<ap:OrgChartSubTopicDefaultsGroup Level="0">
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffffffff"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Topic" ReadOnly="false" TextAlignment="urn:mindjet:Center" TextCapitalization="urn:mindjet:None" VerticalTextAlignment="urn:mindjet:Top">
<ap:Font Bold="true" Color="ff4b4b4b" Italic="false" Name="Verdana" Size="9." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape Dirty="0000000000000000" VerticalBottomMargin="1." VerticalLeftMargin="1." VerticalRightMargin="1." VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="1."/>
<ap:DefaultCalloutFloatingTopicShape Dirty="0000000000000000" VerticalBottomMargin="2." VerticalCalloutFloatingTopicShape="urn:mindjet:RectangleBalloon" VerticalLeftMargin="2." VerticalRightMargin="2." VerticalTopMargin="2."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" MinimumHeight="5." Padding="1." TopicLayoutHorizontalAlignment="urn:mindjet:Center" TopicLayoutVerticalAlignment="urn:mindjet:Center" TopicTextAndImagePosition="urn:mindjet:TextRightImageLeft" TopicWidthControl="urn:mindjet:AutoWidth" Width="50."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="3." SubTopicsAlignment="urn:mindjet:Bottom" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:Elbow" SubTopicsDepth="1" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsShapeWidthFactor="1." SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="3." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
<ap:DefaultSubTopicsVisibility Dirty="0000000000000000" Hidden="false"/>
</ap:OrgChartSubTopicDefaultsGroup>
<ap:OrgChartSubTopicDefaultsGroup Level="1">
<ap:DefaultColor Dirty="0000000000000000" FillColor="ffffffff"/>
<ap:DefaultText Dirty="0000000000000000" PlainText="Topic" ReadOnly="false" TextAlignment="urn:mindjet:Center" TextCapitalization="urn:mindjet:None" VerticalTextAlignment="urn:mindjet:Top">
<ap:Font Bold="false" Color="ff282828" Italic="false" Name="Verdana" Size="9." Strikethrough="false" Underline="false"/>
</ap:DefaultText>
<ap:DefaultSubTopicShape BottomMargin="1." Dirty="0000000000000000" LeftMargin="1." RightMargin="1." SubTopicShape="urn:mindjet:Rectangle" TopMargin="1." VerticalBottomMargin="0.5" VerticalLeftMargin="0.5" VerticalRightMargin="0.5" VerticalSubTopicShape="urn:mindjet:Rectangle" VerticalTopMargin="0.5"/>
<ap:DefaultCalloutFloatingTopicShape Dirty="0000000000000000" VerticalBottomMargin="2." VerticalCalloutFloatingTopicShape="urn:mindjet:RectangleBalloon" VerticalLeftMargin="2." VerticalRightMargin="2." VerticalTopMargin="2."/>
<ap:DefaultTopicLayout Dirty="0000000000000000" MinimumHeight="5." Padding="1." TopicLayoutHorizontalAlignment="urn:mindjet:Center" TopicLayoutVerticalAlignment="urn:mindjet:Center" TopicTextAndImagePosition="urn:mindjet:TextRightImageLeft" TopicWidthControl="urn:mindjet:AutoWidth" Width="50."/>
<ap:DefaultSubTopicsShape Dirty="0000000000000000" DistanceBetweenSiblings="1.3999999761581421" DistanceFromParent="3." SubTopicsAlignment="urn:mindjet:Bottom" SubTopicsAlignmentDualVertical="urn:mindjet:Center" SubTopicsConnectionPoint="urn:mindjet:Outside" SubTopicsConnectionStyle="urn:mindjet:Elbow" SubTopicsDepth="1" SubTopicsGrowth="urn:mindjet:Horizontal" SubTopicsGrowthDirection="urn:mindjet:AutomaticHorizontal" SubTopicsShape="urn:mindjet:Vertical" SubTopicsShapeWidthFactor="1." SubTopicsVerticalAlignment="urn:mindjet:Middle" SubTopicsVerticalGrowthDirection="urn:mindjet:AutomaticVertical" VerticalDistanceBetweenSiblings="1." VerticalDistanceFromParent="3." VerticalSubTopicsConnectionPoint="urn:mindjet:Outside" VerticalSubTopicsConnectionStyle="urn:mindjet:Elbow"/>
</ap:OrgChartSubTopicDefaultsGroup>
<ap:RelationshipDefaultsGroup>
<ap:DefaultColor Dirty="0000000000000000" FillColor="00000000" LineColor="ffe0666e"/>
<ap:DefaultLineStyle Dirty="0000000000000000" LineDashStyle="urn:mindjet:Dash" LineWidth="1.5"/>
<ap:DefaultConnectionStyle ConnectionShape="urn:mindjet:NoArrow" Dirty="0000000000000000" Index="0"/>
<ap:DefaultConnectionStyle ConnectionShape="urn:mindjet:Arrow" Dirty="0000000000000000" Index="1"/>
<ap:DefaultRelationshipLineShape Dirty="0000000000000000" LineShape="urn:mindjet:Bezier"/>
</ap:RelationshipDefaultsGroup>
<ap:BoundaryDefaultsGroup>
<ap:DefaultLineStyle Dirty="0000000000000000" LineDashStyle="urn:mindjet:Solid" LineWidth="1.5"/>
<ap:DefaultBoundaryShape BoundaryShape="urn:mindjet:CurvedLine" Dirty="0000000000000000" Margin="0."/>
</ap:BoundaryDefaultsGroup>
<ap:Structure Dirty="0000000000000000" FadeNotSelectedObjects="true" HideCollapseSign="false" MainTopicLineWidth="0.60000002384185791" MinimumMainTopicsHeight="40." ParentChildSpacing="0." SiblingSpacing="0." StructureGrowthDirection="urn:mindjet:Automatic" UseAutoLayout="true" UseCurveAntialiasing="true" UseOrganicLines="false" UseTextAntialiasing="true" VerticalMainTopicLineWidth="1."/>
<ap:BackgroundFill FillColor="ffc8fdd9"/>
<ap:NotesDefaultFont Color="ff000000" Dirty="0000000000000000" Name="Verdana" Size="10."/>
</ap:StyleGroup>
<ap:MarkersSetGroup>
<ap:IconMarkersSets>
<ap:IconMarkersSet Dirty="0000000000000000" Gen="0000000000000000" OId="KywUsopU1UCwqkJOGN2t3g==">
<ap:Name Dirty="0000000000000000" Name="Flags"/>
<ap:IconMarkers>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="vHB8MbpLpESbZQ7ff6PHcQ==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Yes"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagGreen"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="Hs671SgCNEO4OLRFCo6O/g==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Maybe"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagYellow"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="/clBXKyYoUKYWdVEvZ0rAw==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Discuss"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagOrange"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="Z2cINOZBX0e0vFFUv/AVvA==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Risk"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagRed"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="Ou1OrX9UGUyILoj6LUMbfw==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Move"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagPurple"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="B09r+JSdPkeddhsFn1KCPg==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Defer"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagBlue"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="fqJOKQCRKUWDHXu6MG7zmQ==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="No"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:FlagBlack"/>
</ap:IconMarker>
</ap:IconMarkers>
</ap:IconMarkersSet>
<ap:IconMarkersSet Dirty="0000000000000000" Gen="0000000000000000" OId="Uk0QR6Yh0UCN3bsfg7U7Ow==">
<ap:Name Dirty="0000000000000000" Name="Arrows"/>
<ap:IconMarkers>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="FVOLr2m1PEW/k4LrSwHHig==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Up"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ArrowUp"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="RnBh9uLNZ0KaWgvjps4tyA==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Down"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ArrowDown"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="WJOkMfOFtkC/GsOdC7bmmw==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Left"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ArrowLeft"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="w/jUXln0FUWWUbcw4rBO8Q==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Right"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ArrowRight"/>
</ap:IconMarker>
</ap:IconMarkers>
</ap:IconMarkersSet>
<ap:IconMarkersSet Dirty="0000000000000000" Gen="0000000000000000" OId="M4i5tYHKrEmqCCOxg/uQMg==">
<ap:Name Dirty="0000000000000000" Name="Smileys"/>
<ap:IconMarkers>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="+nrZO70TXUWwD4MMILOrwA==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Happy"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:SmileyHappy"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="R80LwJZ3Y0CYR6y0QZiZPA==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Neutral"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:SmileyNeutral"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="A6WA/uKxU0GqLy/T3gbSJA==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Sad"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:SmileySad"/>
</ap:IconMarker>
</ap:IconMarkers>
</ap:IconMarkersSet>
</ap:IconMarkersSets>
<ap:IconMarkers>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="4m3GM4PjzkyPB6IRNvsv8g==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Pro"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ThumbsUp"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="zPMapRvzD06ybMUxY+ku5g==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Con"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ThumbsDown"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="G537yVYfJUCvgAfHTxuK8Q==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Question"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:QuestionMark"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="6/KnMWw1oU2CZSU9PzyQjQ==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Attention"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:ExclamationMark"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="l1H6C5MlPUWFTZfIZwuhkA==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Decision"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:JudgeHammer"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="wO4UtEvFOUGVceNaTP2TQg==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Date"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:Calendar"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="Z37Ong7GNEijLxXv38yS9w==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Cost"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:Dollar"/>
</ap:IconMarker>
<ap:IconMarker Dirty="0000000000000000" Gen="0000000000000000" OId="bVN9jPRZXESLz6ftrOIJfQ==" xsi:type="ap:StockIconMarker">
<ap:Name Dirty="0000000000000000" Name="Alarm"/>
<ap:OneStockIcon Dirty="0000000000000000" IconType="urn:mindjet:Emergency"/>
</ap:IconMarker>
</ap:IconMarkers>
<ap:FillColorMarkersName Dirty="0000000000000000" Name="Fill Colors"/>
<ap:TextColorMarkersName Dirty="0000000000000000" Name="Font Colors"/>
<ap:TaskPercentageMarkersName Dirty="0000000000000000" Name="Progress"/>
<ap:TaskPercentageMarkers>
<ap:TaskPercentageMarker Dirty="0000000000000000" Gen="0000000000000000" OId="wfTm6FPukUWUh6roju2GWg==">
<ap:Name Dirty="0000000000000000" Name="Not done"/>
<ap:TaskPercentage Dirty="0000000000000000" TaskPercentage="0"/>
</ap:TaskPercentageMarker>
<ap:TaskPercentageMarker Dirty="0000000000000000" Gen="0000000000000000" OId="WizkcjaF1kWuTM+NtAKYSw==">
<ap:Name Dirty="0000000000000000" Name="Quarter done"/>
<ap:TaskPercentage Dirty="0000000000000000" TaskPercentage="25"/>
</ap:TaskPercentageMarker>
<ap:TaskPercentageMarker Dirty="0000000000000000" Gen="0000000000000000" OId="/VY5Cenxg0+a7swWb7g6Wg==">
<ap:Name Dirty="0000000000000000" Name="Half done"/>
<ap:TaskPercentage Dirty="0000000000000000" TaskPercentage="50"/>
</ap:TaskPercentageMarker>
<ap:TaskPercentageMarker Dirty="0000000000000000" Gen="0000000000000000" OId="IK9XHps0Ukqsa3BdYy/+aQ==">
<ap:Name Dirty="0000000000000000" Name="Three quarters done"/>
<ap:TaskPercentage Dirty="0000000000000000" TaskPercentage="75"/>
</ap:TaskPercentageMarker>
<ap:TaskPercentageMarker Dirty="0000000000000000" Gen="0000000000000000" OId="PGiifKBt0U+qNB9+rL7T7w==">
<ap:Name Dirty="0000000000000000" Name="Task done"/>
<ap:TaskPercentage Dirty="0000000000000000" TaskPercentage="100"/>
</ap:TaskPercentageMarker>
</ap:TaskPercentageMarkers>
<ap:TaskPriorityMarkersName Dirty="0000000000000000" Name="Priority"/>
<ap:TaskPriorityMarkers>
<ap:TaskPriorityMarker Dirty="0000000000000000" Gen="0000000000000000" OId="85FfICk8OUq05pJovmxeYg==">
<ap:Name Dirty="0000000000000000" Name="Priority 1"/>
<ap:TaskPriority Dirty="0000000000000000" TaskPriority="urn:mindjet:Prio1"/>
</ap:TaskPriorityMarker>
<ap:TaskPriorityMarker Dirty="0000000000000000" Gen="0000000000000000" OId="kJVB9WuFf0WGQrntzH++iA==">
<ap:Name Dirty="0000000000000000" Name="Priority 2"/>
<ap:TaskPriority Dirty="0000000000000000" TaskPriority="urn:mindjet:Prio2"/>
</ap:TaskPriorityMarker>
<ap:TaskPriorityMarker Dirty="0000000000000000" Gen="0000000000000000" OId="sZPd7LIto02O9jAxadM9HQ==">
<ap:Name Dirty="0000000000000000" Name="Priority 3"/>
<ap:TaskPriority Dirty="0000000000000000" TaskPriority="urn:mindjet:Prio3"/>
</ap:TaskPriorityMarker>
<ap:TaskPriorityMarker Dirty="0000000000000000" Gen="0000000000000000" OId="FNXlJYp3bUSkBETHUQf1WQ==">
<ap:Name Dirty="0000000000000000" Name="Priority 4"/>
<ap:TaskPriority Dirty="0000000000000000" TaskPriority="urn:mindjet:Prio4"/>
</ap:TaskPriorityMarker>
<ap:TaskPriorityMarker Dirty="0000000000000000" Gen="0000000000000000" OId="LFsQivRAkkqtQat366hNdg==">
<ap:Name Dirty="0000000000000000" Name="Priority 5"/>
<ap:TaskPriority Dirty="0000000000000000" TaskPriority="urn:mindjet:Prio5"/>
</ap:TaskPriorityMarker>
</ap:TaskPriorityMarkers>
</ap:MarkersSetGroup>
</ap:Map>
'''

xmind_mainfest_xml_text = b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<manifest xmlns="urn:xmind:xmap:xmlns:manifest:1.0" password-hint="">
<file-entry full-path="content.xml" media-type="text/xml"/>
<file-entry full-path="META-INF/" media-type=""/>
<file-entry full-path="META-INF/manifest.xml" media-type="text/xml"/>
<file-entry full-path="meta.xml" media-type="text/xml"/>
<file-entry full-path="styles.xml" media-type="text/xml"/>
</manifest>
'''

def xmind_meta_xml_func():
    return b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<meta xmlns="urn:xmind:xmap:xmlns:meta:2.0" version="2.0">
<Author>
<Name>User</Name>
<Email/>
<Org/>
</Author>
<Create>
<Time>''' + str(datetime.datetime.now())[:19].encode('utf-8') + b'''</Time>
</Create>
<Creator>
<Name>XMind</Name>
<Version>R3.7.8.201807240049</Version>
</Creator>
<Thumbnail>
<Origin>
<X>0</X>
<Y>0</Y>
</Origin>
<BackgroundColor>#FFFFFF</BackgroundColor>
</Thumbnail>
</meta>
'''

def xmind_styles_xml_func(generateID, themeID):
    return b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-styles xmlns="urn:xmind:xmap:xmlns:style:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" version="2.0">
<automatic-styles>
<style id="5jqolgsls2i30kolk2ko6k11u4" name="" type="topic">
<topic-properties border-line-color="#558ED5" border-line-width="3pt" fo:font-family="Microsoft YaHei" line-class="org.xmind.branchConnection.curve" line-color="#558ED5" line-width="1pt"/>
</style>
<style id="6cvgr0qju6q8e0p3tg4qtl906d" name="" type="summary">
<summary-properties line-color="#C3D69B" line-width="5pt" shape-class="org.xmind.summaryShape.square"/>
</style>
<style id="6ctbd7js1ad8lvlejpp16fts78" name="" type="boundary">
<boundary-properties fo:color="#FFFFFF" fo:font-family="Microsoft YaHei" fo:font-size="10pt" fo:font-style="italic" line-color="#77933C" line-pattern="dot" line-width="3pt" shape-class="org.xmind.boundaryShape.roundedRect" svg:fill="#C3D69B" svg:opacity=".2"/>
</style>
<style id="7020lk96mmo9o8s930cd53l1ku" name="" type="topic">
<topic-properties border-line-color="#F1BD51" border-line-width="2pt" fo:font-family="Microsoft YaHei" svg:fill="#FBF09C"/>
</style>
<style id="7q7eqeead7kmnqllq47iq25dpt" name="" type="topic">
<topic-properties border-line-color="#558ED5" border-line-width="5pt" fo:color="#376092" fo:font-family="Microsoft YaHei" line-class="org.xmind.branchConnection.curve" line-color="#558ED5" line-width="1pt" shape-class="org.xmind.topicShape.roundedRect" svg:fill="#DCE6F2"/>
</style>
<style id="77igj8uue56l9si24o04ipe2fn" name="" type="topic">
<topic-properties border-line-color="#558ED5" border-line-width="2pt" fo:color="#17375E" fo:font-family="Microsoft YaHei" line-class="org.xmind.branchConnection.curve" line-color="#558ED5" line-width="1pt" shape-class="org.xmind.topicShape.roundedRect" svg:fill="#DCE6F2"/>
</style>
<style id="50virqmb3d6ks7ieucd4qt95ei" name="" type="topic">
<topic-properties border-line-width="0pt" fo:color="#FFFFFF" fo:font-family="Microsoft YaHei" fo:font-size="10pt" fo:font-style="italic" line-class="org.xmind.branchConnection.curve" shape-class="org.xmind.topicShape.roundedRect" svg:fill="#77933C"/>
</style>
<style id="6vb5fmrancd010dn1gvgf9q8b5" name="" type="topic">
<topic-properties border-line-width="0pt" fo:color="#FFFFFF" fo:font-family="Microsoft YaHei" fo:font-weight="bold" line-color="#558ED5" svg:fill="#558ED5"/>
</style>
<style id="7llfve2q91rdgneg3gjmhdn4af" name="" type="relationship">
<relationship-properties arrow-end-class="org.xmind.arrowShape.triangle" fo:color="#595959" fo:font-family="Microsoft YaHei" fo:font-size="10pt" fo:font-style="italic" fo:font-weight="normal" fo:text-decoration="none" line-color="#77933C" line-pattern="dash" line-width="3pt"/>
</style>
<style id="6quqd6orfk6o7bsh1o7gmdluqm" name="" type="map">
<map-properties color-gradient="none" line-tapered="none" multi-line-colors="none" svg:fill="#FFFFFF"/>
</style>
</automatic-styles>
<master-styles>
<style id="''' + themeID + b'''" name="Professional" type="theme">
<theme-properties>
<default-style style-family="subTopic" style-id="5jqolgsls2i30kolk2ko6k11u4"/>
<default-style style-family="summary" style-id="6cvgr0qju6q8e0p3tg4qtl906d"/>
<default-style style-family="boundary" style-id="6ctbd7js1ad8lvlejpp16fts78"/>
<default-style style-family="calloutTopic" style-id="7020lk96mmo9o8s930cd53l1ku"/>
<default-style style-family="centralTopic" style-id="7q7eqeead7kmnqllq47iq25dpt"/>
<default-style style-family="mainTopic" style-id="77igj8uue56l9si24o04ipe2fn"/>
<default-style style-family="summaryTopic" style-id="50virqmb3d6ks7ieucd4qt95ei"/>
<default-style style-family="floatingTopic" style-id="6vb5fmrancd010dn1gvgf9q8b5"/>
<default-style style-family="relationship" style-id="7llfve2q91rdgneg3gjmhdn4af"/>
<default-style style-family="map" style-id="6quqd6orfk6o7bsh1o7gmdluqm"/>
</theme-properties>
</style>
</master-styles>
</xmap-styles>
'''

xmind_content_xml_text_head = b'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink" modified-by="User" '''

zen_content_xml_text = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?><xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:xlink="http://www.w3.org/1999/xlink" modified-by="bruce" timestamp="1503058545540" version="2.0"><sheet id="7abtd0ssc7n4pi1nu6i7b6lsdh" modified-by="bruce" theme="0kdeemiijde6nuk97e4t0vpp54" timestamp="1503058545540"><topic id="1vr0lcte2og4t2sopiogvdmifc" modified-by="bruce" structure-class="org.xmind.ui.logic.right" timestamp="1503058545417"><title>Warning\n\xe8\xad\xa6\xe5\x91\x8a\nAttention\nWarnung\n\xea\xb2\xbd\xea\xb3\xa0</title><children><topics type="attached"><topic id="71h1aip2t1o8vvm0a41nausaar" modified-by="bruce" timestamp="1503058545423"><title svg:width="500">This file can not be opened normally, please do not modify and save, otherwise the contents will be permanently lost\xef\xbc\x81</title><children><topics type="attached"><topic id="428akmkh9a0tog6c91qj995qdl" modified-by="bruce" timestamp="1503058545427"><title>You can try using XMind 8 Update 3 or later version to open</title></topic></topics></children></topic><topic id="2kb87f8m38b3hnfhp450c7q35e" modified-by="bruce" timestamp="1503058545434"><title svg:width="500">\xe8\xaf\xa5\xe6\x96\x87\xe4\xbb\xb6\xe6\x97\xa0\xe6\xb3\x95\xe6\xad\xa3\xe5\xb8\xb8\xe6\x89\x93\xe5\xbc\x80\xef\xbc\x8c\xe8\xaf\xb7\xe5\x8b\xbf\xe4\xbf\xae\xe6\x94\xb9\xe5\xb9\xb6\xe4\xbf\x9d\xe5\xad\x98\xef\xbc\x8c\xe5\x90\xa6\xe5\x88\x99\xe6\x96\x87\xe4\xbb\xb6\xe5\x86\x85\xe5\xae\xb9\xe5\xb0\x86\xe4\xbc\x9a\xe6\xb0\xb8\xe4\xb9\x85\xe6\x80\xa7\xe4\xb8\xa2\xe5\xa4\xb1\xef\xbc\x81</title><children><topics type="attached"><topic id="3m9hoo4a09n53ofl6fohdun99f" modified-by="bruce" timestamp="1503058545438"><title>\xe4\xbd\xa0\xe5\x8f\xaf\xe4\xbb\xa5\xe5\xb0\x9d\xe8\xaf\x95\xe4\xbd\xbf\xe7\x94\xa8 XMind 8 Update 3 \xe6\x88\x96\xe6\x9b\xb4\xe6\x96\xb0\xe7\x89\x88\xe6\x9c\xac\xe6\x89\x93\xe5\xbc\x80</title></topic></topics></children></topic><topic id="7r3r4617hvh931ot9obi595r8f" modified-by="bruce" timestamp="1503058545444"><title svg:width="500">\xe8\xa9\xb2\xe6\x96\x87\xe4\xbb\xb6\xe7\x84\xa1\xe6\xb3\x95\xe6\xad\xa3\xe5\xb8\xb8\xe6\x89\x93\xe9\x96\x8b\xef\xbc\x8c\xe8\xab\x8b\xe5\x8b\xbf\xe4\xbf\xae\xe6\x94\xb9\xe4\xb8\xa6\xe4\xbf\x9d\xe5\xad\x98\xef\xbc\x8c\xe5\x90\xa6\xe5\x89\x87\xe6\x96\x87\xe4\xbb\xb6\xe5\x85\xa7\xe5\xae\xb9\xe5\xb0\x87\xe6\x9c\x83\xe6\xb0\xb8\xe4\xb9\x85\xe6\x80\xa7\xe4\xb8\x9f\xe5\xa4\xb1\xef\xbc\x81</title><children><topics type="attached"><topic id="691pgka6gmgpgkacaa0h3f1hjb" modified-by="bruce" timestamp="1503058545448"><title>\xe4\xbd\xa0\xe5\x8f\xaf\xe4\xbb\xa5\xe5\x98\x97\xe8\xa9\xa6\xe4\xbd\xbf\xe7\x94\xa8 XMind 8 Update 3 \xe6\x88\x96\xe6\x9b\xb4\xe6\x96\xb0\xe7\x89\x88\xe6\x9c\xac\xe6\x89\x93\xe9\x96\x8b</title></topic></topics></children></topic><topic id="0f2e3rpkfahg4spg4nda946r0b" modified-by="bruce" timestamp="1503058545453"><title svg:width="500">\xe3\x81\x93\xe3\x81\xae\xe6\x96\x87\xe6\x9b\xb8\xe3\x81\xaf\xe6\xad\xa3\xe5\xb8\xb8\xe3\x81\xab\xe9\x96\x8b\xe3\x81\x8b\xe3\x81\xaa\xe3\x81\x84\xe3\x81\xae\xe3\x81\xa7\xe3\x80\x81\xe4\xbf\xae\xe6\xad\xa3\xe3\x81\x97\xe3\x81\xa6\xe4\xbf\x9d\xe5\xad\x98\xe3\x81\x97\xe3\x81\xaa\xe3\x81\x84\xe3\x82\x88\xe3\x81\x86\xe3\x81\xab\xe3\x81\x97\xe3\x81\xa6\xe3\x81\x8f\xe3\x81\xa0\xe3\x81\x95\xe3\x81\x84\xe3\x80\x82\xe3\x81\x9d\xe3\x81\x86\xe3\x81\xa7\xe3\x81\xaa\xe3\x81\x84\xe3\x81\xa8\xe3\x80\x81\xe6\x9b\xb8\xe9\xa1\x9e\xe3\x81\xae\xe5\x86\x85\xe5\xae\xb9\xe3\x81\x8c\xe6\xb0\xb8\xe4\xb9\x85\xe3\x81\xab\xe5\xa4\xb1\xe3\x82\x8f\xe3\x82\x8c\xe3\x81\xbe\xe3\x81\x99\xe3\x80\x82\xef\xbc\x81</title><children><topics type="attached"><topic id="4vuubta53ksc1falk46mevge0t" modified-by="bruce" timestamp="1503058545457"><title>XMind 8 Update 3 \xe3\x82\x84\xe6\x9b\xb4\xe6\x96\xb0\xe7\x89\x88\xe3\x82\x92\xe4\xbd\xbf\xe3\x81\xa3\xe3\x81\xa6\xe9\x96\x8b\xe3\x81\x8f\xe3\x81\x93\xe3\x81\xa8\xe3\x82\x82\xe3\x81\xa7\xe3\x81\x8d\xe3\x81\xbe\xe3\x81\x99</title></topic></topics></children></topic><topic id="70n9i4u3lb89sq9l1m1bs255j5" modified-by="bruce" timestamp="1503058545463"><title svg:width="500">Datei kann nicht richtig ge\xc3\xb6ffnet werden. Bitte \xc3\xa4ndern Sie diese Datei nicht und speichern Sie sie, sonst wird die Datei endg\xc3\xbcltig gel\xc3\xb6scht werden.</title><children><topics type="attached"><topic id="1qpc5ee298p2sqeqbinpca46b7" modified-by="bruce" timestamp="1503058545466"><title svg:width="500">Bitte versuchen Sie, diese Datei mit XMind 8 Update 3 oder sp\xc3\xa4ter zu \xc3\xb6ffnen.</title></topic></topics></children></topic><topic id="4dmes10uc19pq7enu8sc4bmvif" modified-by="bruce" timestamp="1503058545473"><title svg:width="500">Ce fichier ne peut pas ouvert normalement, veuillez le r\xc3\xa9diger et sauvegarder, sinon le fichier sera perdu en permanence. </title><children><topics type="attached"><topic id="5f0rivgubii2launodiln7sdkt" modified-by="bruce" timestamp="1503058545476"><title svg:width="500">Vous pouvez essayer d\'ouvrir avec XMind 8 Update 3 ou avec une version plus r\xc3\xa9cente.</title></topic></topics></children></topic><topic id="10pn1os1sgfsnqa8akabom5pej" modified-by="bruce" timestamp="1503058545481"><title svg:width="500">\xed\x8c\x8c\xec\x9d\xbc\xec\x9d\x84 \xec\xa0\x95\xec\x83\x81\xec\xa0\x81\xec\x9c\xbc\xeb\xa1\x9c \xec\x97\xb4 \xec\x88\x98 \xec\x97\x86\xec\x9c\xbc\xeb\xa9\xb0, \xec\x88\x98\xec\xa0\x95 \xeb\xb0\x8f \xec\xa0\x80\xec\x9e\xa5\xed\x95\x98\xec\xa7\x80 \xeb\xa7\x88\xec\x8b\xad\xec\x8b\x9c\xec\x98\xa4. \xea\xb7\xb8\xeb\xa0\x87\xec\xa7\x80 \xec\x95\x8a\xec\x9c\xbc\xeb\xa9\xb4 \xed\x8c\x8c\xec\x9d\xbc\xec\x9d\x98 \xeb\x82\xb4\xec\x9a\xa9\xec\x9d\xb4 \xec\x98\x81\xea\xb5\xac\xec\xa0\x81\xec\x9c\xbc\xeb\xa1\x9c \xec\x86\x90\xec\x8b\xa4\xeb\x90\xa9\xeb\x8b\x88\xeb\x8b\xa4!</title><children><topics type="attached"><topic id="0l2nr0fq3em22rctapkj46ue58" modified-by="bruce" timestamp="1503058545484"><title svg:width="500">XMind 8 Update 3 \xeb\x98\x90\xeb\x8a\x94 \xec\x9d\xb4\xed\x9b\x84 \xeb\xb2\x84\xec\xa0\x84\xec\x9d\x84 \xec\x82\xac\xec\x9a\xa9\xed\x95\x98\xec\x97\xac</title></topic></topics></children></topic></topics></children><extensions><extension provider="org.xmind.ui.map.unbalanced"><content><right-number>-1</right-number></content></extension></extensions></topic><title>Sheet 1</title></sheet></xmap-content>'
def zen_metadata_json_func(activeSheetId):
    return b'{"creator":{"name":"Vana","version":"10.0.0.201911260056"},"activeSheetId":"' + activeSheetId.encode('ascii') + b'"}\n'

def zen_content_json_func(sheet_map_id, root_topic_title):
    return \
[{'id': sheet_map_id,
  'class': 'sheet',
  'title': 'Map 1',
  'rootTopic': {'id': 'b9aa22deba98b3b20c7ac8aca2',
   'class': 'topic',
   'title': root_topic_title,
   'structureClass': 'org.xmind.ui.map.unbalanced',
   'titleUnedited': True,
   'extensions': [{'content': [{'content': '3', 'name': 'right-number'}],
     'provider': 'org.xmind.ui.map.unbalanced'}]},
  'theme': {'id': '6518e97a4149b5f96691ab3b5d',
   'importantTopic': {'type': 'topic',
    'properties': {'fo:font-weight': 'bold',
     'fo:color': '#333333',
     'svg:fill': '#FFFF00'}},
   'minorTopic': {'type': 'topic',
    'properties': {'fo:font-weight': 'bold',
     'fo:color': '#333333',
     'svg:fill': '#FFCB88'}},
   'expiredTopic': {'type': 'topic',
    'properties': {'fo:font-style': 'italic',
     'fo:text-decoration': ' line-through'}},
   'centralTopic': {'properties': {'fo:font-family': 'NeverMind',
     'fo:font-weight': '600',
     'fo:font-style': 'normal',
     'fo:font-size': '28pt',
     'shape-class': 'org.xmind.topicShape.roundedRect',
     'svg:fill': '#0288D1',
     'line-class': 'org.xmind.branchConnection.curve',
     'line-width': '2',
     'line-color': '#333333',
     'border-line-width': '0'},
    'styleId': '9a94e1a0-7e67-48df-a231-7fa0c60b7b97',
    'type': 'topic'},
   'boundary': {'properties': {'fo:font-family': 'NeverMind',
     'fo:color': '#FFFFFF',
     'fo:font-weight': '500',
     'svg:fill': '#D5E9FC',
     'shape-class': 'org.xmind.boundaryShape.roundedRect',
     'line-pattern': 'dash',
     'line-color': '#0288D1',
     'fo:font-style': 'normal',
     'fo:font-size': '13pt'},
    'styleId': '94a6c549-690c-4f1e-b18f-457f114abcb0',
    'type': 'boundary'},
   'floatingTopic': {'properties': {'fo:font-family': 'NeverMind',
     'fo:font-weight': '600',
     'fo:font-size': '13pt',
     'shape-class': 'org.xmind.topicShape.roundedRect',
     'svg:fill': '#333333',
     'fo:font-style': 'normal',
     'fo:color': '#FFFFFF',
     'border-line-width': '0',
     'border-line-color': 'none',
     'line-class': 'org.xmind.branchConnection.roundedElbow',
     'line-width': '1',
     'line-color': '#333333'},
    'styleId': '8286b472-0630-4970-8bf1-510a831dc2b9',
    'type': 'topic'},
   'subTopic': {'properties': {'fo:font-weight': '500',
     'fo:text-align': 'left',
     'fo:font-family': 'NeverMind',
     'line-class': 'org.xmind.branchConnection.roundedElbow',
     'fo:font-style': 'normal',
     'fo:font-size': '13pt',
     'fo:color': '#333333',
     'svg:fill': 'none',
     'shape-class': 'org.xmind.topicShape.underline'},
    'styleId': 'ddd92ae3-f2b4-48ee-9e47-2dacee6acac4',
    'type': 'topic'},
   'mainTopic': {'properties': {'fo:font-weight': '600',
     'fo:font-family': 'NeverMind',
     'fo:font-style': 'normal',
     'fo:font-size': '20pt',
     'line-class': 'org.xmind.branchConnection.roundedElbow',
     'line-width': '1',
     'line-color': '#333333',
     'border-line-width': '2',
     'border-line-color': '#333333'},
    'styleId': '7565fe37-2200-4483-b343-91bdf53e563e',
    'type': 'topic'},
   'calloutTopic': {'properties': {'fo:font-family': 'NeverMind',
     'fo:font-weight': '600',
     'fo:font-style': 'normal',
     'callout-shape-class': 'org.xmind.calloutTopicShape.balloon.roundedRect',
     'fo:font-size': '13pt',
     'fo:color': '#FFFFFF'},
    'styleId': '9bffcc6a-0526-4db5-b304-ea3830a42846',
    'type': 'topic'},
   'summaryTopic': {'properties': {'fo:font-family': 'NeverMind',
     'fo:font-weight': '600',
     'fo:font-size': '13pt',
     'shape-class': 'org.xmind.topicShape.roundedRect',
     'svg:fill': '#333333',
     'border-line-width': '1',
     'border-line-color': 'none',
     'fo:font-style': 'normal',
     'line-class': 'org.xmind.branchConnection.roundedElbow',
     'line-width': '1',
     'line-color': '#333333'},
    'styleId': 'a82dc72d-29bc-4d81-bd44-3f1bee0ed35c',
    'type': 'topic'},
   'relationship': {'properties': {'fo:font-family': 'NeverMind',
     'fo:font-weight': 'normal',
     'line-color': '#0288D1',
     'shape-class': 'org.xmind.relationshipShape.curved',
     'line-width': '2',
     'fo:font-size': '13pt',
     'fo:color': '#333333'},
    'styleId': '1611e291-8cc1-4500-93a5-69281d5bedf0',
    'type': 'relationship'},
   'map': {'type': 'map',
    'styleId': '7e90467a-d643-4fa9-84f2-f8f0166e5afb',
    'properties': {}},
   'summary': {'type': 'summary',
    'styleId': '8aa88864-8667-4627-a763-a84973e0109b',
    'properties': {'line-color': '#0288D1',
     'shape-class': 'org.xmind.summaryShape.round',
     'line-width': '2'}}},
  'topicPositioning': 'fixed'}]


class mindmapDocument:
    def load(self, file):
        '''
            从文件中读取数据
            读出来的数据保存到 m_data 中
            返回值是读取是否成功，格式不正确则返回 False
            m_data 的格式是
                m_data = [["根节点内容", 是否折叠起来, [子节点1, 子节点2, ...]]]
                子节点的格式是 ["节点内容", 是否折叠起来, [子节点1, 子节点2, ...]]
        '''
        assert False
        
    def save(self, file):
        '''
            将内容保存到文件，保存为什么格式由派生类决定
        '''
        assert False

    def attach(self, document):
        self.m_data = document.m_data
        
    def clear(self):
        del self.m_data

class textDocument(mindmapDocument):
    def load(self, file):
        # Open file as text file.
        with open(file, 'r', encoding='utf-8') as f:
            try:
                lines = f.read().split('\n')
            except UnicodeDecodeError as e:
                return False
        
        i = 0
        def addNodes(node_list, depth):
            nonlocal i
            while i < len(lines):
                line = lines[i]
                
                topic_text_vt = line.lstrip('\t')
                n_tab = len(line) - len(topic_text_vt)
                if n_tab < depth:
                    break
                if n_tab - depth > 1:
                    return False
                
                topic_text = topic_text_vt.lstrip('\v')
                if len(topic_text) == 0:
                    i += 1
                    continue
                
                topic_foded = len(topic_text) != len(topic_text_vt)
                
                if n_tab == depth:
                    node_list.append([topic_text, topic_foded, []])
                    i += 1
                else:
                    if len(node_list) == 0:
                        return False
                    if not addNodes(node_list[len(node_list)-1][2], depth + 1):
                        return False
            
            return True

        self.m_data = []
        if not addNodes(self.m_data, 0):
            return False
        
        return True
        

    def save(self, file):
        try:
            with open(file, 'w') as f:
                def writeTree(nodelist, depth):
                    for node in nodelist:
                        f.write('\t' * depth + ('\v' if node[1] else '') + node[0] + '\n')
                        writeTree(node[2], depth + 1)
                writeTree(self.m_data, 0)
        except Exception as e:
            sys.stderr.write(str(e) + "\n")
            return False
        return True

class mindjetDocument(mindmapDocument):
    def load(self, file):
        # Open the file as zip file.
        if not zipfile.is_zipfile(file):
            return False
        with zipfile.ZipFile(file, 'r') as zf:
            # Check files as mindjets document.
            if len(zf.filelist) != 1 or zf.filelist[0].filename != 'Document.xml':
                return False

            # Open the main xml file.
            xml_text = zf.read('Document.xml')

        def __getDomElemNodeNameSubElem(elem, nodeName):
            childNodes = elem.childNodes
            for node in childNodes:
                if node.nodeName == nodeName:
                    return node
            return None

        def __getDomElemNodeNameSubElemList(elem, nodeName):
            childNodes = elem.childNodes
            result = []
            for node in childNodes:
                if node.nodeName == nodeName:
                    result.append(node)
            return result

        # Find the root topic
        root_elem = xml.dom.minidom.parseString(xml_text).documentElement
        if root_elem.nodeName != 'ap:Map':
            sys.stderr.write(msg_not_a_valid_file % ('mindjet' + msg_document) + msg_has_no % "'ap:Map'" + "\n")
            return False
        OneTopic_elem = __getDomElemNodeNameSubElem(root_elem, 'ap:OneTopic')
        if OneTopic_elem is None:
            sys.stderr.write(msg_not_a_valid_file % ('mindjet' + msg_document) + msg_has_no % "'ap:OneTopic'" + "\n")
            return False
        del root_elem

        def addNodes(node_list, topics_elem):
            topic_elem_list = __getDomElemNodeNameSubElemList(topics_elem, 'ap:Topic')
            for topic_elem in topic_elem_list:
                topic_collapsed = False
                view_elem = __getDomElemNodeNameSubElem(topic_elem, 'ap:TopicViewGroup')
                if view_elem is not None:
                    Collapsed_elem = __getDomElemNodeNameSubElem(view_elem, 'ap:Collapsed')
                    if Collapsed_elem is not None and Collapsed_elem.hasAttribute('Collapsed'):
                        Collapsed_text = Collapsed_elem.getAttribute('Collapsed')
                        if Collapsed_text == 'true':
                            topic_collapsed = True
                text_elem = __getDomElemNodeNameSubElem(topic_elem, 'ap:Text')
                if text_elem is None or not text_elem.hasAttribute('PlainText'):
                    return False
                topic_text = text_elem.getAttribute('PlainText').strip()
                sub_topic_list = []
                sub_topic_elem = __getDomElemNodeNameSubElem(topic_elem, 'ap:SubTopics')
                if sub_topic_elem is not None:
                    if not addNodes(sub_topic_list, sub_topic_elem):
                        return False
                node_list.append([topic_text, topic_collapsed, sub_topic_list])
            return True

        self.m_data = []
        if not addNodes(self.m_data, OneTopic_elem):
            return False
        
        return True
        
    def save(self, file):
        def generateMapID():
            return base64.b64encode(bytes(map(lambda x:random.randrange(256), range(16))))

        id_dict = set()
        def generateID():
            # 生成并确保去重
            id_value = random.randrange(9**8)
            while id_value in id_dict:
                id_value = random.randrange(9**8)
            id_dict.add(id_value)
            
            # 转换为字符串
            d = b'00000000'
            base = tuple(9**i for i in range(7,-1,-1))
            for i in range(8):
                d += bytes((id_value // base[i],))
                id_value %= base[i]
            return base64.b64encode(d)
        
        Document_xml_text = mindjet_Document_xml_head_func(generateMapID)
        
        def appendTopic(topic_list, depth):
            nonlocal Document_xml_text
            for topic in topic_list:
                Document_xml_text += b'<ap:Topic OId="' + generateID() + b'">'
                if len(topic[2]) > 0:
                    Document_xml_text += b'<ap:SubTopics>'
                    appendTopic(topic[2] , depth + 1)
                    Document_xml_text += b'</ap:SubTopics>'
                if topic[1]:
                    Document_xml_text += b'<ap:TopicViewGroup ViewIndex="0"><ap:Collapsed Collapsed="true"/></ap:TopicViewGroup>'
                else:
                    Document_xml_text += b'<ap:TopicViewGroup ViewIndex="0"/>'
                Document_xml_text += b'<ap:Text PlainText="' + topic[0].encode('utf-8').replace(b'<', b'&lt;').replace(b'>', b'&gt;') + b'"><ap:Font/><ap:FontRange From="0" To="' + str(len(topic[0])-1).encode('utf-8') + b'"/></ap:Text>'
                if depth > 0:
                    Document_xml_text += b'<ap:Offset CX="40.00"/><ap:SubTopicShape SubTopicShape="urn:mindjet:' + (b'RoundedRectangle' if depth < 3 else b'Line') + b'"/>'
                Document_xml_text += b'</ap:Topic>'

        appendTopic(self.m_data, 0)
        Document_xml_text += mindjet_Document_xml_text_tail

        try:
            with zipfile.ZipFile(file, 'w') as zf:
                zf.writestr('Document.xml', Document_xml_text, zipfile.ZIP_DEFLATED)
        except Exception as e:
            sys.stderr.write(str(e) + "\n")
            return False
        
        return True

class xmindDocument(mindmapDocument):
    def load(self, file):
        # Open the file as zip file.
        if not zipfile.is_zipfile(file):
            return False
        with zipfile.ZipFile(file, 'r') as zf:
            # Check files as xmind document.
            if len(zf.filelist) < 4 or 'content.xml' not in zf.namelist():
                return False

            # Open the main xml file.
            xml_text = zf.read('content.xml')

        def __getDomElemNodeNameSubElem(elem, nodeName):
            childNodes = elem.childNodes
            for node in childNodes:
                if node.nodeName == nodeName:
                    return node
            return None

        def __getDomElemNodeNameSubElemList(elem, nodeName):
            childNodes = elem.childNodes
            result = []
            for node in childNodes:
                if node.nodeName == nodeName:
                    result.append(node)
            return result

        # Find the root topic
        root_elem = xml.dom.minidom.parseString(xml_text).documentElement
        if root_elem.nodeName != 'xmap-content':
            sys.stderr.write(msg_not_a_valid_file % ('xmind' + msg_document) + msg_has_no % "'xmap-content'" + "\n")
            return False
        sheet_elem = __getDomElemNodeNameSubElem(root_elem, 'sheet')
        if sheet_elem is None:
            sys.stderr.write(msg_not_a_valid_file % ('xmind' + msg_document) + msg_has_no % "'sheet'" + "\n")
            return False
        del root_elem

        def addNodes(node_list, topics_elem):
            topic_elem_list = __getDomElemNodeNameSubElemList(topics_elem, 'topic')
            for topic_elem in topic_elem_list:
                topic_foded = False
                if topic_elem.hasAttribute('branch'):
                    branch_text = topic_elem.getAttribute('branch')
                    if branch_text == 'folded':
                        topic_foded = True
                title_elem = __getDomElemNodeNameSubElem(topic_elem, 'title')
                if title_elem is None:
                    return False
                data_text = __getDomElemNodeNameSubElem(title_elem, '#text')
                if data_text is None:
                    return False
                topic_text = data_text.data.strip()
                sub_topic_list = []
                children_elem = __getDomElemNodeNameSubElem(topic_elem, 'children')
                if children_elem is not None:
                    sub_topics_elem = __getDomElemNodeNameSubElem(children_elem, 'topics')
                    if not addNodes(sub_topic_list, sub_topics_elem):
                        return False
                node_list.append([topic_text, topic_foded, sub_topic_list])
            return True

        self.m_data = []
        if not addNodes(self.m_data, sheet_elem):
            return False
        
        return True
        
    def save(self, file):
        
        def generateID():
            d = chr(random.randint(ord('0'), ord('7'))).encode('utf-8')
            for i in range(25):
                r = random.randint(ord('0'), ord('0') + 32 - 1)
                if r > ord('9'):
                    r += ord('a') - ord('9') - 1
                d += chr(r).encode('utf-8')
            return d

        timestamp = str(int(time.time() * 1000)).encode('utf-8')
        themeID = b'23dsnfno6clq7b4qusal5s0hnt'
        
        content_xml_text = xmind_content_xml_text_head
        content_xml_text += b'timestamp="' + timestamp + b'" version="2.0">'
        content_xml_text += b'<sheet id="' + generateID() + b'" modified-by="User" theme="' + themeID + b'" timestamp="' + timestamp + b'">'
        
        def appendTopic(topic_list, depth):
            nonlocal content_xml_text
            for topic in topic_list:
                content_xml_text += b'<topic ' + (b'branch="folded" ' if topic[1] else b'') + b'id="' + generateID() + b'" modified-by="User" ' + (b'structure-class="org.xmind.ui.map.unbalanced" ' if depth == 0 else b'') + b'timestamp="' + timestamp + b'">'
                content_xml_text += b'<title>' + topic[0].encode('utf-8').replace(b'<', b'&lt;').replace(b'>', b'&gt;') + b'</title>'
                if len(topic[2]) > 0:
                    content_xml_text += b'<children>'
                    content_xml_text += b'<topics type="attached">'
                    appendTopic(topic[2], depth + 1)
                    content_xml_text += b'</topics>'
                    content_xml_text += b'</children>'
                if depth == 0:
                    content_xml_text += b'<extensions><extension provider="org.xmind.ui.map.unbalanced"><content><right-number>1</right-number></content></extension></extensions>'
                content_xml_text += b'</topic>'

        appendTopic(self.m_data, 0)
        content_xml_text += b'<title>Sheet 1</title></sheet></xmap-content>'
        
        style_xml_text = xmind_styles_xml_func(generateID, themeID)
        meta_xml_text = xmind_meta_xml_func()
        
        try:
            with zipfile.ZipFile(file, 'w') as zf:
                zf.writestr('META-INF/manifest.xml', xmind_mainfest_xml_text, zipfile.ZIP_DEFLATED)
                zf.writestr('meta.xml', meta_xml_text, zipfile.ZIP_DEFLATED)
                zf.writestr('styles.xml', style_xml_text, zipfile.ZIP_DEFLATED)
                zf.writestr('content.xml', content_xml_text, zipfile.ZIP_DEFLATED)
        except Exception as e:
            sys.stderr.write(str(e) + "\n")
            return False
        
        return True


class xmindZenDocument(mindmapDocument):
    def load(self, file):
        # Open the file as zip file.
        if not zipfile.is_zipfile(file):
            return False
        with zipfile.ZipFile(file, 'r') as zf:
            # Check files as xmind document.
            if len(zf.filelist) < 4 or 'content.json' not in zf.namelist():
                return False

            # Open the main json file.
            json_text = zf.read('content.json')

        try:
            json_obj = json.loads(json_text)
            root_topic = json_obj[0]['rootTopic']
            del json_text, json_obj
        except(json.JSONDecodeError, IndexError, TypeError, KeyError):
            sys.stderr.write(msg_not_a_valid_file % ('xmind-zen' + msg_document) + msg_error_format_in % "content.json" + "\n")
            return False
        
        def addNodes(node_list, children):
            if 'attached' not in children:
                return True
            for topic_elem in children['attached']:
                topic_foded = 'branch' in topic_elem and topic_elem['branch'] == 'folded'
                
                if 'title' in topic_elem:
                    topic_text = topic_elem['title']
                else:
                    topic_text = ''
                
                sub_topic_list = []
                if 'children' in topic_elem:
                    if not addNodes(sub_topic_list, topic_elem['children']):
                        return False
                node_list.append([topic_text, topic_foded, sub_topic_list])
            return True

        root_children_list = []
        if 'children' in root_topic:
            if not addNodes(root_children_list, root_topic['children']):
                return False
        if 'title' not in root_topic:
            root_topic['title'] = ''
        self.m_data = [[root_topic['title'], False, root_children_list]]
        
        return True
        
    def save(self, file):
        def generateUUID():
            return uuid.uuid3(uuid.uuid4(), 'xmind-zen uuid ' + str(time.time_ns()))
        
        def generateID():
            return hex(random.randrange(16**26))[2:]
        
        sheet_map_id = generateID()
        
        metadata_json_data = zen_metadata_json_func(sheet_map_id)
        content_json = zen_content_json_func(sheet_map_id, self.m_data[0][0])
        
        def addChildren(topic_dict, children_list):
            children_topic_list = []
            for child in children_list:
                c_topic_dict = {
                    "id": generateID(),
                    "title": child[0],
                    "titleUnedited": True,
                }
                if child[1]:
                    c_topic_dict['branch'] = 'folded'
                addChildren(c_topic_dict, child[2])
                children_topic_list.append(c_topic_dict)
            topic_dict["children"] = {"attached": children_topic_list}
        
        addChildren(content_json[0]['rootTopic'], self.m_data[0][2])
        
        content_json_text = json.dumps(content_json, ensure_ascii = False)
        manifest_json_data = b'{"file-entries":{"content.json":{},"metadata.json":{}}}'
        
        try:
            with zipfile.ZipFile(file, 'w') as zf:
                zf.writestr('manifest.json', manifest_json_data, zipfile.ZIP_DEFLATED)
                zf.writestr('metadata.json', metadata_json_data, zipfile.ZIP_DEFLATED)
                zf.writestr('content.json', content_json_text, zipfile.ZIP_DEFLATED)
                zf.writestr('content.xml', zen_content_xml_text, zipfile.ZIP_DEFLATED)
        except Exception as e:
            sys.stderr.write(str(e) + "\n")
            return False
            
        return True
        
def main(args):
    if not os.path.exists(args.src):
        sys.stderr.write(msg_no_such_file % args.src + '\n')
        return 1
    if not os.path.isfile(args.src):
        sys.stderr.write(msg_is_directory % args.src + '\n')
        return 1
    xmind = xmindDocument()
    zen = xmindZenDocument()
    mmap = mindjetDocument()
    txt = textDocument()
    listDocumentObj = [zen, xmind, mmap, txt]  # zen 必须在 xmind 之前
    objData = None
    for obj in listDocumentObj:
        if obj.load(args.src):
            objData = obj
            break
    if objData is None:
        sys.stderr.write(msg_load_failed_file % args.src + '\n')
        return 1
    
    if args.dest is None:
        print(args.desc_type_dict[{
            xmind: 'xmind',
            zen: 'zen',
            txt: 'txt',
            mmap: 'mmap',
        }[objData]])
        return 0
    
    objDest = {
        'txt':txt,
        'xmind':xmind,
        'mmap':mmap,
        'zen' :zen,
    }[args.type]
    objDest.attach(objData)
    if not objDest.save(args.dest):
        sys.stderr.write(msg_write_failed_file % args.dest + '\n')
        return 1
    return 0

if __name__ == '__main__':
    desc_type_dict = {
        'xmind': 'xmind - XMind 8 ' + msg_document,
        'zen': 'zen - XMind zen ' + msg_document,
        'txt': 'txt - txt ' + msg_document,
        'mmap': 'mmap - Mindjet maps ' + msg_document,
    }
    
    parser = argparse.ArgumentParser(description = msg_argument_description)
    parser.add_argument('src', help=msg_arg_src)
    parser.add_argument('dest', help=msg_arg_dest, nargs='?')
    parser.add_argument(
        '--type', '-t', help=msg_arg_type + '; '.join([desc_type_dict[k] for k in desc_type_dict]),
        choices=['txt', 'mmap', 'xmind', 'zen'],
        default='txt'
        )
    args = parser.parse_args()
    args.desc_type_dict = desc_type_dict

    exit(main(args))

