define([
	'jquery',
	'app/lib/ember',
	'app/application',
	'app/controller/accounts'
], function($, Ember, Application, AccountsController) {
	Application.AccountsView = Ember.View.extend({
		controller: AccountsController
	});

	return Application.AccountsView;
});