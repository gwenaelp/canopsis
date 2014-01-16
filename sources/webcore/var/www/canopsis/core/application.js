define(function(require, exports, module) {
	Ember.TEMPLATES['application'] = Ember.Handlebars.compile(require('app/text!app/templates/application.html'));

	var Application = Ember.Application.create({});

	Application.Router.map(function() {
		this.route('canopsis', { path: '/'});
	});

	return Application;
});