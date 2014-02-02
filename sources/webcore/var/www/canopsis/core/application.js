define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data'
], function($, Ember, DS) {
	var Application = Ember.Application.create({});

	Application.register("transform:array", DS.ArrayTransform);

	Application.AuthenticatedRoute = Ember.Route.extend({
		beforeModel: function(transition) {
			if(!this.controllerFor('login').get('authkey')) {
				this.loginRequired(transition);
			}
		},

		loginRequired: function(transition) {
			console.log('Login required');

			this.controllerFor('login').setProperties({
				'attempt': transition,
				'content': {
					errors: [{
						message: "You don't have enough permissions to access this view."
					}]
				}
			});

			this.transitionTo('login');
		},

		actions: {
			error: function(reason, transition) {
				if(reason.status === 403 || reason.status === 401) {
					this.loginRequired(transition);
				}
			}
		}
	});

	Application.Router.map(function() {
		this.resource('login');

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
		findAll: function(store, type) {
			return type.findAll(store, localStorage.cps_authkey);
		}
	});

	Application.ApplicationSerializer = DS.RESTSerializer.extend({
		extractFindAll: function(store, type, payload) {
			return type.extractFindAll(store, payload);
		}
	})

	return Application;
});