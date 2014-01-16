define(function(require, exports, module) {
	var Application = require('app/application');

	Ember.TEMPLATES['canopsis'] = Ember.Handlebars.compile(require('app/text!app/templates/canopsis.html'));

	Application.CanopsisRoute = Ember.Route.extend({});
	Application.CanopsisController = Ember.Controller.extend({});
});