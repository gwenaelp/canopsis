define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'jquery.encoding.digests.sha1'
], function($, Ember, Application) {
	Application.LoginRoute = Ember.Route.extend({
		setupController: function(controller, model) {
			controller.reset();
		}
	});

	Application.LoginController = Ember.ObjectController.extend({
		content: {},

		reset: function() {
			this.setProperties({
				username: "",
				password: "",
				shadow: "",
				cryptedkey: "",
				authkey: localStorage.cps_authkey
			});
		},

		authkey: localStorage.cps_authkey,
		authkeyChanged: function() {
			localStorage.cps_authkey = this.get('authkey');
		}.observes('authkey'),

		actions: {
			login: function() {
				this.set('shadow', $.encoding.digests.hexSha1Str(this.get('password')));

				/* generate salt for authkey */
				var salt = new Date();
				salt = salt.getTime() / 10000;
				salt = parseInt(salt) * 10;
				salt = salt.toString();

				this.set('cryptedkey', $.encoding.digests.hexSha1Str(this.get('shadow') + salt));

				/* start authentication */
				this.auth_crypt();
			}
		},

		auth_crypt: function() {
			console.log('Trying CRYPT-auth...');

			var promise = $.get('/auth', {
				cryptedKey: true,
				login: this.get('username'),
				password: this.get('cryptedkey')
			});

			promise.done(this.loggedIn.bind(this));
			promise.fail(this.auth_shadow.bind(this));
		},

		auth_shadow: function() {
			console.log('Trying Shadow-auth...');

			var promise = $.get('/auth', {
				shadow: true,
				login: this.get('username'),
				password: this.get('shadow')
			});

			promise.done(this.loggedIn.bind(this));
			promise.fail(this.auth_plain.bind(this));
		},

		auth_plain: function() {
			console.log('Trying PLAIN-auth...');

			var promise = $.get('/auth', {
				login: this.get('username'),
				password: this.get('password')
			});

			promise.done(this.loggedIn.bind(this));
			promise.fail(this.loginFailed.bind(this));
		},

		loggedIn: function(response) {
			this.set('authkey', response.data[0].authkey);

			var transition = this.get('attempt');

			if(transition) {
				transition.retry();
				this.set('attempt', null);
			}
			else {
				this.transitionToRoute('/run/dashboard');
			}
		},

		loginFailed: function() {
			this.set('content', {
				errors: [{
					message: 'Bad login/password'
				}]
			});
			this.transitionToRoute('/login');
		}
	});

	return Application.LoginController;
});