# -*- coding: utf-8 -*-
import sublime, sublime_plugin, string, re

bases = {'binary' : 2,'octal' : 8,'decimal' : 10, 'hexadecimal' : 16};

class NumberObj(object):
	def __init__(self, number, base):
		self.oldNumber = number;
		self.number = int(number, bases[base]);
		self.base = base;
	def getNumber(self):
		if self.base == 'binary':
			return removeLetterFromLong(str(bin(self.number)[2:]));
		if self.base == 'octal':
			return removeLetterFromLong(str(oct(self.number)[2:]));
		if self.base == 'decimal':
			return removeLetterFromLong(str(self.number));
		if self.base == 'hexadecimal':
			return removeLetterFromLong(str(hex(self.number)[2:]));

def removeLetterFromLong(line):
	if line[len(line) - 1].lower() == 'l':
		return line[:-1];
	else:
		return line;

def putEndLines(arr):
	arr = [str(x) + '\n' for x in arr];
	arr[-1] = arr[-1][:-1];
	return arr;

def removeEmptyString(arr):
	return filter(None, arr);

def writeToView(self, region, conteneur):
	if len(conteneur) != 0:
		if self.estSelect:
			self.view.replace(self.edit, region, ''.join(putEndLines(conteneur)));
		else:
			self.view.erase(self.edit, sublime.Region(0, self.view.size()));
			self.view.insert(self.edit, 0, ''.join(putEndLines(conteneur)));
	else:
		print("CodingUtils error: No string found !");


class CodeutiCommand(sublime_plugin.TextCommand):

	def getArrayFromRegex(self, line, reg):
		if reg == 'octal': return re.findall(r'[0-7]+', line);
		elif reg == 'binary': return re.findall(r'[01]+', line);
		elif reg == 'decimal': return re.findall(r'[+-]?\d+(?:\.\d+)?', line);
		elif reg == 'hexadecimal': return  re.findall(r'(?:0[xX])?[0-9a-fA-F]+', line);
		elif reg == 'string' : return re.findall(r'[a-zA-Z]+', line);
		#Thanks to John Gruber for this awesome regex for urls
		#http://daringfireball.net/2010/07/improved_regex_for_matching_urls
		elif reg == 'url' : return re.findall(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""", line);
		else: return [];

	def removeStrings(self, contenue):
		conteneur = [];
		splitter = '';

		if self.settings.get('put_splitter_between_multiple_numbers'):  
			splitter = self.settings.get('splitter_between_multiple_numbers');

		for line in contenue:
				if self.util == 'keepOct': conteneur.append(splitter.join(self.getArrayFromRegex(line, 'octal')));
				if self.util == 'keepBin': conteneur.append(splitter.join(self.getArrayFromRegex(line, 'binary')));
				if self.util == 'keepDec': conteneur.append(splitter.join(self.getArrayFromRegex(line, 'decimal')));
				if self.util == 'keepHex': conteneur.append(splitter.join(self.getArrayFromRegex(line, 'hexadecimal')));
				
		return removeEmptyString(conteneur);

	def removeNumbers(self, contenue):
		conteneur = [];
		for line in contenue:
			if self.settings.get('put_splitter_between_multiple_strings'):
				conteneur.append(self.settings.get('splitter_between_multiple_strings').join(self.getArrayFromRegex(line, 'string')));
			else:
				conteneur.append(''.join(self.getArrayFromRegex(line, 'string')));
		return removeEmptyString(conteneur);

	def extractUrl(self, contenue):
		conteneur = [];

		for line in contenue:
			urls = self.getArrayFromRegex(line, 'url');

			if len(urls) != 0:
				for url in urls:
					#Remove all non ASCII characters
					conteneur.append(''.join([x for x in url[0] if ord(x) < 128]));

		return conteneur;

	def removeIdcLines(self, contenue):
		return list(set(contenue));

	def run(self, edit, util = 'keepDecimal'):
		lines = [];
		result = [];
		view = self.view;
		self.edit = edit; 
		self.util = util;
		self.settings = sublime.load_settings("CodingUtils.sublime-settings");

		if view.sel()[0].empty() and len(view.sel()) == 1: #No selection
			self.estSelect = False;

			if util == 'remIdcLines':
				result = self.removeIdcLines([x for x in view.substr(sublime.Region(0, self.view.size())).splitlines() if x != '']);
			if util == 'keepUrl':
				result = self.extractUrl([x for x in view.substr(sublime.Region(0, self.view.size())).splitlines() if x != '']);
			if util == 'keepOct' or util == 'keepBin' or util == 'keepDec' or util == 'keepHex':
				result = self.removeStrings([x for x in view.substr(sublime.Region(0, self.view.size())).splitlines() if x != '']);
			if util == 'keepLet':
				result = self.removeNumbers([x for x in view.substr(sublime.Region(0, self.view.size())).splitlines() if x != '']);

			writeToView(self, view.sel()[-1].end(), result);
		else:
			self.estSelect = True;
			for region in view.sel():
				if region.empty():
					continue;
				else:
					if util == 'remIdcLines':
						result = self.removeIdcLines([x for x in view.substr(region).splitlines() if x != '']);
					if util == 'keepUrl':
						result = self.extractUrl([x for x in view.substr(region).splitlines() if x != '']);
					if util == 'keepOct' or util == 'keepBin' or util == 'keepDec' or util == 'keepHex':
						result = self.removeStrings([x for x in view.substr(region).splitlines() if x != '']);
					if util == 'keepLet':
						result = self.removeNumbers([x for x in view.substr(region).splitlines() if x != '']);

					writeToView(self, region, result);