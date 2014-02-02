define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/model/account'
], function($, Ember, Application, Account) {
	Application.AccountsRoute = Application.AuthenticatedRoute.extend({
		setupController: function(controller, model) {
			controller.set('content', {
				'toolitems': controller.toolbar,
				'accounts': model
			});
		},

		model: function() {
			return this.store.findAll('account');
		}
	});

	Application.AccountsController = Ember.ObjectController.extend({
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
				this.set('content', {
					toolitems: this.toolbar,
					accounts: this.store.findAll('account')
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
			}
		}
	});

	return Application.AccountsController;
});