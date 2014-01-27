define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data'
], function($, Ember, DS) {
	var Application = Ember.Application.create({});

	Application.register("transform:array", DS.ArrayTransform);

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

	Application.ApplicationAdapter = DS.RESTAdapter.extend({
		buildUrl: function(type, id) {
			if(type === 'account') {
				return '/' + type + '/' + id;
			}

			return this._super(type, id);
		}
	});

	return Application;
});