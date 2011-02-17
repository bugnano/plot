#! /usr/bin/env python
# -*- coding: ascii -*-

# Copyright (c) 2010, Franco Bugnano
# All rights reserved.
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#     1. The origin of this software must not be misrepresented; you must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     appreciated but is not required.
#
#     2. Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
#
#     3. This notice may not be removed or altered from any source
#     distribution.

from __future__ import division

import wx


class PlotCanvas(wx.Panel):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name='plotCanvas'):
		wx.Panel.__init__(self, parent, id, pos, size, style, name)

		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
		self.max_x = 1
		self.max_y = 1
		self.str_f = '%d'
		self.str_max_x = '%d' % self.max_x
		self.str_max_y = self.str_f % self.max_y

		self.plots = []

		self.Bind(wx.EVT_PAINT, self.OnPaint)


	def SetMax(self, max_x, max_y):
		self.max_x = max_x
		self.max_y = max_y
		self.str_max_x = '%d' % self.max_x
		self.str_max_y = self.str_f % self.max_y


	def SetFormat(self, str_f):
		self.str_f = str_f
		self.str_max_y = self.str_f % self.max_y


	def AddPlot(self, colour):
		plot = PlotData(colour)

		self.plots.append(plot)

		return plot


	def OnPaint(self, event):
		dc = wx.AutoBufferedPaintDC(self)

		self.Draw(dc)


	def UpdatePlot(self):
		if self.IsDoubleBuffered():
			dc = wx.ClientDC(self)
		else:
			dc = wx.BufferedDC(wx.ClientDC(self))

		self.Draw(dc)


	def Draw(self, dc):
		width_dc, height_dc = dc.GetSizeTuple()

		dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
		dc.Clear()

		dc.SetTextBackground(self.GetBackgroundColour())
		dc.SetTextForeground(self.GetForegroundColour())
		dc.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

		padleft, pady = dc.GetTextExtent('M' * (len(self.str_max_y) + 1))
		padright, pady = dc.GetTextExtent('M' * (int(len(self.str_max_x) / 2) + 1))
		left = padleft
		top = 2 * pady
		width = width_dc - (padleft + padright)
		height = height_dc - (2 * top)
		text_bottom = top + height + ((pady * 1) / 4)

		dc.SetPen(wx.Pen(self.GetForegroundColour()))
		dc.SetBrush(wx.BLACK_BRUSH)
		dc.DrawRectangle(left, top-2, width, height+2)

		# Valori degli assi
		wt, ht = dc.GetTextExtent(self.str_max_y)
		text_right = (left * 7) / 8
		dc.DrawText(self.str_max_y, text_right - wt, top - (ht / 2))

		wt, ht = dc.GetTextExtent('0')
		dc.DrawText('0', left - (wt / 2), text_bottom)

		wt, ht = dc.GetTextExtent(self.str_max_x)
		dc.DrawText(self.str_max_x, (left + width) - (wt / 2), text_bottom)

		# Disegno i punti intermedi
		dc.SetPen(wx.Pen(wx.Colour(0x40, 0x40, 0x40), 1, wx.DOT))

		for i in range(1, 5):
			val = self.max_y - (self.max_y * (i / 5))
			y = top + ((height * i) / 5)
			dc.DrawLine(left, y, left + width, y)

			wt, ht = dc.GetTextExtent(self.str_f % val)
			dc.DrawText(self.str_f % val, text_right - wt, y - (ht / 2))

		for i in range(1, 6):
			val = self.max_x * (i / 6)
			x = left + ((width * i) / 6)
			dc.DrawLine(x, top, x, top + height)

			wt, ht = dc.GetTextExtent('%d' % val)
			dc.DrawText('%d' % val, x - (wt / 2), text_bottom)

		# Disegno tutti i plot associati
		for plot in self.plots:
			plot.Draw(dc, left, top, width, height, self.max_x, self.max_y)

		# Ridisegno il quadrato che contiene il grafico
		dc.SetPen(wx.Pen(self.GetForegroundColour()))
		dc.SetBrush(wx.TRANSPARENT_BRUSH)
		dc.DrawRectangle(left, top-2, width, height+2)


class PlotData(object):
	def __init__(self, colour):
		self.colour = colour
		self.data = []

	def SetData(self, data):
		self.data = data

	def Draw(self, dc, left, top, width, height, max_x, max_y):
		dc.SetPen(wx.Pen(self.colour, 1, wx.SOLID))
		dati_normalizzati = [(max_y if y > max_y else (0 if y < 0 else y)) for y in list(self.data)[:max_x]]
		scala_y = height / max_y
		lista_y = [((max_y - y) * scala_y) for y in dati_normalizzati]
		passo = width / max_x
		lista_punti = [wx.Point(left + (i * passo) + 1, top + e - 1) for i, e in enumerate(lista_y)]
		if len(lista_punti) > 2:
			dc.DrawSpline(lista_punti)
		else:
			dc.DrawLines(lista_punti)

