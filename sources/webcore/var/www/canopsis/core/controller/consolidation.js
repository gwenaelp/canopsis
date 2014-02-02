define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/model/consolidation'
], function($, Ember, Application, Consolidation) {
	Application.ConsolidationRoute = Application.AuthenticatedRoute.extend({
		setupController: function(controller, model) {
			controller.set('content', {
				toolitems: controller.toolbar,
				consolidations: model
			});
		},

		model: function() {
			return this.store.findAll('consolidation');
		}
	});

	Application.ConsolidationController = Ember.ObjectController.extend({
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
		},{
			title: 'Import',
			action: 'import',
			icon: 'import'
		},{
			title: 'Export',
			action: 'export',
			icon: 'open'
		}],

		actions: {
			do: function(action) {
				this.send(action);
			},

			refresh: function() {
				this.set('content', {
					toolitems: this.toolbar,
					consolidations: this.store.findAll('consolidation')
				});
			},

			add: function() {
				;
			},

			duplicate: function() {
				;
			},

			remove: function() {
				;
			},

			import: function() {
				;
			},

			export: function() {
				;
			}
		}
	});

	return Application.ConsolidationController;
});