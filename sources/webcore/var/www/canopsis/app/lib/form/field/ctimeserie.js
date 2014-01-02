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
		sliding_time: true,
		operation: 'MEAN',
		fill: false,
		forecast: {
			enable: false,
			max_points: 250,
			duration: {value: 0, unit: 'day'},
			enddate: undefined,
			category: NotLinearMidVariable,
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
			fieldLabel: 'Enable',
			parent: this,
			listeners: {
				change: function(field, oldvalue, newvalue, eOpts) {
					void(field);
					void(oldvalue);
					void(eOpts);

					if (newvalue) {
						for (var index=0; index<this.parent.items.items.length; index++) {
							item = this.parent.items.items[index];
							if (item !== this) {
								item.disable();
								item.hide();
							}
						}
					} else {
						for (var index=0; index<this.parent.items.items.length; index++) {
							item = this.parent.items.items[index];
							if (item !== this) {
								item.enable();
								item.show();
							}
						}
					}
				}
			}
		});
		this.ts_max_points = Ext.widget('numberfield', {
			name: 'max_points',
			width: 50,
			value: this.value.max_points,
			minValue: this.max_points_min,
			fieldLabel: 'Max points',
			hidden: true
		});
		this.ts_period = Ext.widget('cperiod', {
			isFormField: false,
			name: 'period',
			value:this.value.period,
			fieldLabel: 'Period',
			hidden: true
		});
		this.ts_sliding_time = Ext.widget('checkbox', {
			name: 'sliding_time',
			value:this.value.sliding_time,
			fieldLabel: 'Sliding time',
			hidden: true
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
			fieldLabel: 'Operation',
			store: {
				xtype: 'store',
				fields: ['value', 'name'],
				data: operation_store_data
			},
			hidden: true
		});
		this.ts_fill = Ext.widget('checkbox', {
			name: 'fill',
			value:this.value.fill,
			fieldLabel: 'Do not cut curve in empty intervals',
			hidden: true
		});
		this.ts_forecast = Ext.widget('cforecast', {
			name: 'forecast',
			value: this.value.forecast,
			fieldLabel: 'Forecast',
			hidden: true
		});

		this.items = [
			this.ts_enable,
			this.ts_max_points,
			this.ts_period,
			this.ts_sliding_time,
			this.ts_operation,
			this.ts_fill,
			this.ts_forecast
		];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		this.callParent(arguments);

		var disabled = value[0].raw.value;

		for (var i=0; i<this.items.items.length; i++) {
			var item = this.items.items[i];
			item.setDisabled(disabled);
		}
	},

	show: function() {
		this.callParent(arguments);

		for (int i=1; i<this.items.items.length; i++) {
			var item = this.items.items[i];
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
