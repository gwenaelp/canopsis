define([
	'jquery',
	'app/lib/ember',
], function($, Ember) {
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