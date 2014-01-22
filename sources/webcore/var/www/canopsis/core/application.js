define(function(require, exports, module) {
	Ember.TEMPLATES['application'] = Ember.Handlebars.compile(require('text!app/templates/application.html'));

	var Application = Ember.Application.create({});

	Application.Router.map(function() {
		this.resource('build', function() {
			this.resource('accounts');
			this.resource('groups');
			this.resource('curves');
			this.resource('perfdata');
			this.resource('selectors');
			this.resource('consolidation');
			this.resource('topologies');
			this.resource('eventfilter');
		});

		this.resource('run', function() {
			this.resource('dashboard');
		});
	});

	return Application;
});