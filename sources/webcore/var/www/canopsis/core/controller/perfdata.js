define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/model/perfdata'
], function($, Ember, Application, Perfdata) {
	Application.PerfdataRoute = Application.AuthenticatedRoute.extend({
		setupController: function(controller, model) {
			controller.set('content', {
				toolitems: controller.toolbar,
				perfdatas: model
			});
		},

		model: function() {
			return this.store.findAll('perfdata');
		}
	});

	Application.PerfdataController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Remove',
			action: 'remove',
			icon: 'trash'
		}],

		actions: {
			do: function(action) {
				this.send(action);
			},

			refresh: function() {
				controller.set('content', {
					'toolitems': this.toolbar,
					'perfdatas': this.store.findAll('perfdata')
				});
			},

			remove: function() {
				;
			}
		}
	});

	return Application.PerfdataController;
});