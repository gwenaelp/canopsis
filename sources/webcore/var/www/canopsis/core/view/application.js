define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/controller/application'
], function($, Ember, Application, ApplicationController) {
	Application.ApplicationView = Ember.View.extend({
		controller: ApplicationController
	});

	return Application.ApplicationView;
});