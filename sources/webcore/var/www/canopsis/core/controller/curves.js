define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/model/curve'
], function($, Ember, Application, Curve) {
	Application.CurvesRoute = Application.AuthenticatedRoute.extend({
		setupController: function(controller, model) {
			controller.set('content', {
				toolitems: controller.toolbar,
				curves: model
			});
		},

		model: function() {
			return this.store.findAll('curve');
		}
	});

	Application.CurvesController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Add',
			action: 'add',
			icon: 'plus-sign'
		},{
			title: 'Duplicate',
			action: 'duplicate',
			icon: 'file'
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
					'curves': this.store.findAll('curve')
				});
			},

			duplicate: function() {
				;
			},

			remove: function() {
				;
			}
		}
	});

	return Application.CurvesController;
});