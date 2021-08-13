/* http://keith-wood.name/keypad.html
   Russian localisation for the jQuery keypad extension
   Written by Uwe Jakobs(u.jakobs{at}imageco.ru) September 2009. */
(function($) { // hide the namespace
	'use strict';
	//tree
    function _switchLayouts(input){
        console.log("SWITCH");
        var lenLay = $.keypad.switchLayouts.length;
        var next = $.keypad.switchCurrentLayout +1;
        if(!(next < lenLay)){
            next = 0
        }
        $.keypad.switchCurrentLayout = next;
        $(input).keypad("option", {
                keypadOnly: false,
                layout: $.keypad.switchLayouts[next]
            });

        //input.focus();
    }

	//текущая позиция
	function currentPosition(_input) {
		var input = _input[0];
		if ('selectionStart' in input) {
            // Standard-compliant browsers
            return  input.selectionStart;
        } else if (document.selection) {
            // IE
            input.focus();
            var sel = document.selection.createRange();
            var selLen = document.selection.createRange().text.length;
            sel.moveStart('character', - input.value.length);
            return sel.text.length - selLen;
        }
    }
	//переместить курсор в позицию
	function moveCursor(input, pos) {
	    setTimeout(function() {
            input[0].focus();
            input[0].setSelectionRange(pos, pos);
        }, 100);
	}
	//переместить в лево на один шаг
	function movePrev(input) {
		var cp = currentPosition(input);
        var toMove = cp ? cp - 1 : 0;
        moveCursor(input, toMove)
    }
    function moveNext(input) {
		var cp = currentPosition(input);
		var cpLen = input.val().length;
        var toMove = cp + 1;
		moveCursor(input, toMove)
    }
	$.keypad.addKeyDef('START', 'start',
    	function(inst) { moveCursor(this, 0); }
    	);
	$.keypad.addKeyDef('END', 'end',
    	function(inst) { moveCursor(this, this.val().length); }
    	);
	$.keypad.addKeyDef('PREV', 'prev',
    	function(inst) {
			movePrev(this);
			//$(this).trigger($.Event("keydown", {keyCode: 37}))
		}
    	);
	$.keypad.addKeyDef('NEXT', 'next',
    	function(inst) {
			moveNext(this);
			//$(this).trigger($.Event("keydown", {keyCode: 39}))
		});
	$.keypad.addKeyDef('SWITCH', 'switch',
        function(inst) { _switchLayouts(this); }
    );

	$.keypad.qwertzAlphabeticRU = ['йцукенгшщзхъ', 'фывапролджэ', 'ячсмитьбю'];
	$.keypad.qwertzAlphabeticEN = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm'];
	// $.keypad.qwertzLayout =
	// 	['!"§$%&/()=?`' + $.keypad.BACK + $.keypad.HALF_SPACE + '$£€/',
	// 	'<>°^@{[]}\\~´;:' + $.keypad.HALF_SPACE + '789*',
	// 	$.keypad.qwertzAlphabetic[0] + '+*' + $.keypad.HALF_SPACE + '456-',
	// 	$.keypad.HALF_SPACE + $.keypad.qwertzAlphabetic[1] + '#\'' + $.keypad.SPACE + '123+',
	// 	'|' + $.keypad.qwertzAlphabetic[2] + 'µ,.-_' + $.keypad.SPACE + $.keypad.HALF_SPACE +'.0,=',
	// 	$.keypad.SHIFT + $.keypad.SPACE + $.keypad.SPACE_BAR  + $.keypad.SPACE + $.keypad.SPACE +
	// 	$.keypad.CLEAR + $.keypad.SPACE + $.keypad.SPACE + $.keypad.HALF_SPACE + $.keypad.CLOSE];

	$.keypad.qwertzLayoutRU = [
		'1234567890'+$.keypad.BACK  + $.keypad.SPACE + $.keypad.START + $.keypad.END,
		$.keypad.qwertzAlphabeticRU[0]+ $.keypad.SPACE + $.keypad.PREV + $.keypad.NEXT,
		$.keypad.HALF_SPACE + $.keypad.qwertzAlphabeticRU[1]+ $.keypad.SPACE + $.keypad.HALF_SPACE + $.keypad.SWITCH,
		$.keypad.SHIFT + $.keypad.qwertzAlphabeticRU[2]+"-",
		"[]"+$.keypad.SPACE_BAR + ",./_"+ $.keypad.CLOSE
	];

	$.keypad.qwertzLayoutEN = [
		'1234567890'+$.keypad.BACK  + $.keypad.SPACE + $.keypad.START + $.keypad.END,
		$.keypad.SPACE + $.keypad.qwertzAlphabeticEN[0]+ $.keypad.SPACE + $.keypad.SPACE + $.keypad.PREV + $.keypad.NEXT,
		$.keypad.SPACE + $.keypad.HALF_SPACE + $.keypad.qwertzAlphabeticEN[1]+ $.keypad.HALF_SPACE+ $.keypad.SPACE +$.keypad.SPACE + $.keypad.SWITCH,
		$.keypad.SHIFT + $.keypad.qwertzAlphabeticEN[2]+"-",
		"[]"+$.keypad.SPACE_BAR + ",./_"+ $.keypad.CLOSE
	];
	$.keypad.symbolLayout = [
	    '1234567890'+$.keypad.BACK  + $.keypad.SPACE + $.keypad.START + $.keypad.END,
        $.keypad.HALF_SPACE +'!@#№$%^&*'+$.keypad.HALF_SPACE + $.keypad.SPACE+ $.keypad.SPACE+ $.keypad.SPACE+ $.keypad.PREV + $.keypad.NEXT,
		'`"\'~;:?=+\\' +$.keypad.SPACE+ $.keypad.SPACE + $.keypad.SPACE + $.keypad.SWITCH,
		$.keypad.SHIFT + '{}()<>'+"-",
		"[]"+$.keypad.SPACE_BAR + ",./_"+ $.keypad.CLOSE
    ];
	$.keypad.switchLayouts = [
        $.keypad.qwertzLayoutRU,
		$.keypad.qwertzLayoutEN,
		$.keypad.symbolLayout
	];
	$.keypad.switchCurrentLayout = 0;
	$.keypad.switchLayout = $.keypad.switchLayouts[$.keypad.switchCurrentLayout];
	$.keypad.regionalOptions.ru = {
		buttonText: '...',
		buttonStatus: 'Открыть клавиатуру',
		closeText: 'Закрыть',
		closeStatus: 'Клавиатура будет закрыта',
		clearText: 'Очистить',
		clearStatus: 'Очищает поле',
		backText: '←',
		backStatus: 'Удалить один символ',
		shiftText: '↑',
		shiftStatus: 'Поднимает первый символ',
		spacebarText: '&nbsp;',
		spacebarStatus: '',
		enterText: 'Enter',
		enterStatus: '',
		tabText: '→',
		tabStatus: '',
		alphabeticLayout: $.keypad.qwertzAlphabetic,
		fullLayout: $.keypad.qwertzLayout,
		isAlphabetic: $.keypad.isAlphabetic,
		isNumeric: $.keypad.isNumeric,
		toUpper: $.keypad.toUpper,
		isRTL: false,
		/*мои кнопки*/
		startText: '↞',
		startStatus: 'Переместиться на старт',
		endText: '↠',
		endStatus: 'Переместиться в конец',
		prevText: '←',
		prevStatus: 'Переместиться на один символ назад',
		nextText: '→',
		nextStatus: 'Переместиться на один символ вперед',
        switchText: 'switch',
		switchStatus: 'Переключить язык'
	};

})(jQuery);
