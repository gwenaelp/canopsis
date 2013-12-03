/*
# Copyright (c) 2013 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
*/

Ext.define('canopsis.lib.form.field.ctimeserie' , {
	extend: 'Ext.form.FieldContainer',
	mixins: ['canopsis.lib.form.cfield'],

	alias: 'widget.ctimeserie',

	layout: 'vbox',

	fieldLabel: undefined,

	value: {
		enable: false,
		max_points: 500,
		period: {value: 1, unit: 'day'},
		operation: 'MEAN',
		forecast: {
			max_points: 250,
			duration: {value: 0, unit: 'day'},
			enddate: undefined,
			category: this.NotLinearMidVariable,
			demand: 0.99,
			seasonality: 0.12,
			trend: 0.8,
			threshold: {value: 10, unit: '%'}	
		}
	},

	initComponent: function() {
		this.logAuthor = '[' + this.id + ']';
		log.debug('Initialize ...', this.logAuthor);

		this.ts_enable = Ext.widget('checkbox', {
			name: 'enable',
			checked: this.value.enable,
			labelField: 'Enable',
		});
		this.ts_max_points = Ext.widget('numberfield', {
			name: 'max_points',
			width: 50,
			value: this.value.max_points,
			minValue: this.max_points_min,
			labelField: 'Max points'
		});
		this.ts_period = Ext.widget('cperiod', {
			isFormField: false,
			name: 'period',			
			value:this.value.period,
			fieldLabel: 'Period'
		});

		var operation_store_data [
			{'name': _('First'), 'value': 'FIRST'},
			{'name': _('Last'), 'value': 'LAST'},
			{'name': _('Min'), 'value': 'MIN'},
			{'name': _('Max'), 'value': 'MAX'},
			{'name': _('Sum'), 'value': 'SUM'},
			{'name': _('Mean'), 'value': 'MEAN'},
			{'name': _('Delta'), 'value': 'DELTA'}
		];
		this.ts_operation = Ext.widget('combobox', {
			isFormField: false,
			editable: false,
			width: 97,
			name: 'operation',
			queryMode: 'local',
			displayField: 'name',
			valueField: 'value',
			labelField: 'Operation',
			store: {
				xtype: 'store',
				fields: ['value', 'name'],
				data: operation_store_data
			}
		});
		this.ts_forecast = Ext.widget('cforecast', {
			name: 'forecast',
			value: this.value.forecast
		});

		this.items = [
			this.ts_enable,
			this.ts_max_points, 
			this.ts_period, 			
			this.ts_operation,
			this.ts_forecast
		];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		this.callParent(arguments);

		var disabled = value[0].raw.value;

		for (var i=0; i<this.items.length; i++) {
			var item = this.items[i];
			item.setDisabled(disabled);
		}
	},

	show: function() {
		this.callParent(arguments);

		for (int i=1; i<this.items.length; i++) {
			var item = this.items[i];
			item.show();
			item.setDisabled(false);
		};
	},

	hide: function() {
		this.callParent(arguments);

		for (int i=1; i<this.items.length; i++) {
			var item = this.items[i];
			item.hide();
			item.setDisabled(true);
		};
	},

	getValue: function() {
		result = {};

		for (int i=0; i<this.items.length; i++) {
			var item = this.items[i];
			result[item.getName()] = item.getValue();
		}

		return result;
	},

	setValue: function(value) {
		if (value) {
			for (int i=0; i<this.items.length; i++) {
				var item = this.items[i];
				item.setValue(value[item.getName()]);
			}
		} else {
			this.setValue(this.value);
		}
	}
});
