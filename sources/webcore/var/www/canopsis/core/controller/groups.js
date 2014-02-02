define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/model/group'
], function($, Ember, Application, Group) {
	Application.GroupsRoute = Application.AuthenticatedRoute.extend({
		setupController: function(controller, model) {
			controller.set('content', {
				toolitems: controller.toolbar,
				groups: model
			});
		},

		model: function() {
			return this.store.findAll('group');
		}
	});

	Application.GroupsController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Add',
			action: 'add',
			icon: 'plus-sign'
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
				this.set('content', {
					toolitems: this.toolbar,
					groups: this.store.findAll('group')
				});
			},

			add: function() {
				;
			},

			remove: function() {
				;
			}
		}
	});

	return Application.GroupsController;
});