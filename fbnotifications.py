from argparse import ArgumentParser
from random import randint
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from subprocess import call
from json import loads
from re import search
import browser_cookie3

class FBNotifications:
	
	def __init__( self, search ):
		self.cookies      = { cookie.name:cookie.value for cookie in browser_cookie3.chrome( domain_name = 'facebook.com' ) }
		self.user_id      = self.cookies['c_user']
		self.regex_search = '({0})'.format( ')|('.join( search ) )
		self.url          = 'https://{0}-edge-chat.facebook.com/pull'.format( randint( 0, 6 ) )
		self.query        = { 'channel':'p_' + self.user_id, 'msgs_recv':'0', 'state':'offline' }
		self.set_sticky()

	def get_new_query( self, fb_json = {} ):
		# Query string with new seq
		if 'seq' in fb_json:
			self.query['seq'] = fb_json['seq']

		if ( ( 'ms' in fb_json ) and ( 'iseq' in fb_json['ms'][0] ) ):
			self.query['isq'] = fb_json['ms'][0]['iseq']

		return self.query

	def set_sticky( self ):
		sticky_query                = self.query.copy()
		sticky_query['msgr_region'] = 'ATN'
		fb_json                     = self.get_json( query = sticky_query )
		self.query['sticky_token']  = fb_json['lb_info']['sticky']
		self.query['sticky_pool']   = fb_json['lb_info']['pool']

	def get_json( self , fb_json = {}, query = None ):
		if query is None:
			query = self.get_new_query( fb_json )

		url      = self.url + '?' + urlencode( query )
		request  = Request( url, headers = { 'Cookie':'c_user={0};xs={1}'.format( self.cookies['c_user'], self.cookies['xs'] ), 'User-Agent':'Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0)', 'Referer':'https://www.facebook.com/', 'cache-control':'no-cache' } )
		response = urlopen( request )
		str_json = response.read().decode( 'utf-8' )[10:]
		return loads( str_json )

	def do_search( self, msgs ):
		for sender, msg in msgs.items():
			if search( self.regex_search , msg ):
				call( [ 'notify-send', sender + ' chamando no messenger' ] )

	def begin( self ):
		fb_json = {}

		while True:
			fb_json = self.get_json( fb_json )

			msgs = {}

			if 'ms' in fb_json:
				for msg_obj in fb_json['ms']:
					if 'message' in msg_obj:
						msgs[ msg_obj['message']['sender_name'] ] = msg_obj['message']['body']
			
			if msgs:
				self.do_search( msgs )
			

def Main():
	parser = ArgumentParser( description = "Executa uma notificação quando um (ou mais) determinado(s) nome(s) é/são chamado(s) no chat do facebook" )
	
	parser.add_argument( 'nome', nargs = '+', help = "Nome que ativará a notificação" )

	args = parser.parse_args()

	fbn = FBNotifications( args.nome )
	fbn.begin()

if __name__ == '__main__':
	Main()
