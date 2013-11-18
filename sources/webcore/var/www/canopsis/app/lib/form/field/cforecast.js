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

Ext.define('canopsis.lib.form.field.cforecast' , {
	extend: 'Ext.form.FieldContainer',
	mixins: ['canopsis.lib.form.cfield'],

	alias: 'widget.cforecast',

	layout: 'vbox',

	enable: false,
	max_points: 250,
	max_points_min: 1,

	duration = {value: 1, unit: 'day'},
	number_step: 1,
	number_min_val: 0,

	value: {unit: 'day', value: 1},
	add_none_value: false,

	fieldLabel: undefined,

	initComponent: function() {
		this.logAuthor = '[' + this.id + ']';
		log.debug('Initialize ...', this.logAuthor);

		this.ts_enable = Ext.widget('checkbox', {
			name: 'forecast_enable',
			checked: this.enable,
			labelField: 'Enable',
		});
		this.ts_max_points = Ext.widget('numberfield', {
			name: 'forecast_max_points',
			width: 50,
			value: this.max_points,
			minValue: this.max_points_min,
			labelField: 'Max points'
		});
		this.ts_duration = Ext.widget('cperiod', {
			isFormField: false,
			name: 'ts_duration',			
			value:this.duration,
			minValue: this.number_min_val,
			fieldLabel: 'Duration (if no max points)'
		});
		this.ts_date = Ext.widget('datefield', {
			name: 'date',
			value: this.date,
			fieldLabel: 'End date (if no max points and no duration',
		});

		this.items = [this.ts_enable, this.ts_max_points, this.ts_duration, this.ts_date];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		if(value[0].raw.value) {
			this.ts_window.setDisabled(false);
		}
		else {
			this.ts_window.setDisabled(true);
		}
	},

	show: function() {
		this.callParent(arguments);
		this.ts_window.show();
		this.ts_window.setDisabled(false);
		this.ts_unit.show();
		this.ts_unit.setDisabled(false);
	},

	hide: function() {
		this.callParent(arguments);
		this.ts_window.hide();
		this.ts_window.setDisabled(true);
		this.ts_unit.hide();
		this.ts_unit.setDisabled(true);
	},

	getValue: function() {
		if(!this.ts_unit.getValue()) {
			return undefined;
		}

		return {value: this.ts_window.getValue(), unit: this.ts_unit.getValue()};
	},

	setValue: function(value) {
		if(value) {
			this.ts_window.setValue(value.value);
			this.ts_unit.setValue(value.unit);
		}
		else {
			this.ts_unit.select(this.ts_unit.getStore().data.items[0]);
		}
	}
});
