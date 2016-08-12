from argparse import ArgumentParser,RawTextHelpFormatter
from multiprocessing import Pool
from re import compile as comp
from requests import get
from lxml import etree
from sys import stdout

parser=ArgumentParser(description='xx\'s Steam group query tool',formatter_class=RawTextHelpFormatter)

parser.add_argument('-v','--verbose',action='store_true',help='run in verbose mode')
parser.add_argument('-t','--tag',metavar='reg',help='regex value to match against tags')
parser.add_argument('-g','--group',metavar='reg',help='regex value to match against group names')
parser.add_argument('-k','--key',metavar='reg',help='regex value to match against body text')
parser.add_argument('-r','--range',metavar='n',nargs=2,type=int,default=[4,100],help='the range of GIDs to search')
parser.add_argument('-w','--workers',metavar='n',type=int,default=5,help='number of workers to use')

args=parser.parse_args()

if not args.tag and not args.group and not args.keyword:
	print 'one of "tag", "group", or "keyword" must be specified'
	exit()

if args.tag: args.tag=comp(args.tag)
if args.key: args.key=comp(args.key)
if args.group: args.group=comp(args.group)

def search(gid):
	doc=etree.HTML(get('http://steamcommunity.com/gid/'+str(gid)).text)
	matches={"tag": None,"group": None,"key": None}

	if args.tag:
		res=doc.xpath('/html/body/div[1]/div[7]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]/span')
		try:
			if len(res)>0:
				if args.tag.match(res[0].text):
					stdout.write('gid '+str(gid)+'\'s tag ('+res[0].text+') matched query\n')
		except Exception as e:
			stdout.write('gid '+str(gid)+'\'s tag could not be retrieved ('+(e.__class__.__name__)+')\n')
	if args.group:
		res=doc.xpath('/html/body/div[1]/div[7]/div[2]/div/div[1]/div/div[1]/div[2]/div[3]')
		try:
			if len(res)>0:
				if args.group.match(res[0].text):
					stdout.write('gid '+str(gid)+'\'s name ('+res[0].text+') matched query\n')
		except Exception as e:
			stdout.write('gid '+str(gid)+'\'s name could not be retrieved ('+(e.__class__.__name__)+')\n')
	if args.key:
		res=doc.xpath('/html/body/div[1]/div[7]/div[2]/div')
		try:
			if len(res)>0:
				if args.key.match(res[0].text):
					stdout.write('gid '+str(gid)+' matched keyword query\n')
		except Exception as e:
			stdout.write('gid '+str(gid)+' could not be retrieved ('+(e.__class__.__name__)+')\n')

if __name__=='__main__':
	pool=Pool(processes=args.workers)
	pool.map(search,range(args.range[0],args.range[1]+1))