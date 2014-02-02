define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/model/selector'
], function($, Ember, Application, Selector) {
	Application.SelectorsRoute = Application.AuthenticatedRoute.extend({
		setupController: function(controller, model) {
			controller.set('content', {
				toolitems: controller.toolbar,
				selectors: model
			});
		},

		model: function() {
			return this.store.findAll('selector');
		}
	});

	Application.SelectorsController = Ember.ObjectController.extend({
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

			derogate: function(id) {
				;
			},

			refresh: function() {
				controller.set('content', {
					'toolitems': this.toolbar,
					'selectors': this.store.findAll('selector')
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

	return Application.SelectorsController;
});