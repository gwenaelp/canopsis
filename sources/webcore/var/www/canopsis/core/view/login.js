define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/controller/login'
], function($, Ember, Application, LoginController) {
	Application.LoginView = Ember.View.extend({
		controller: LoginController
	});

	return Application.LoginView;
});