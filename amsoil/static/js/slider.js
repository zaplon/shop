$.widget( "geekman.slider", {

    // Default options.
    options: {
        value: 0
    },
    effects: ['top','left', 'right'],
    offsets: ['10px','20px','40px'],
    currentSlide: 0,
    _create: function() {
        this.slidesList = this.element.find('ul');
        this.arrowLeft = this.element.find('.slide-left');
        this.arrowRight = this.element.find('.slide-right');
        this.lastNavigated = 0;

        var me = this;

        this.arrowLeft.click(function(){
           me.navigate(-1);
        });
        this.arrowRight.click(function(){
           me.navigate(1);
        });

        var lis = this.slidesList.children()
        this.slidesList.children().css('display','none');
        $(lis[0]).css('display','block');

        this.hideSlideElements();
        this.animateSlide();

        //window.setInterval(function(){ me.navigate(1); }, 5000);

    },
    hideSlideElements: function(){

        var ch = this.slidesList.children();

        var text = $(ch[this.currentSlide]).find('.text');
        var buttons = $(ch[this.currentSlide]).find('.buttons');
        var title = $(ch[this.currentSlide]).find('.title');
        text.css('opacity','0');
        buttons.css('opacity','0');
        title.css('opacity','0');
    },
    animateSlide: function(){

        var ch = this.slidesList.children();

        var text = $(ch[this.currentSlide]).find('.text');
        var buttons = $(ch[this.currentSlide]).find('.buttons');
        var title = $(ch[this.currentSlide]).find('.title');
        var e1 = this.effects[Math.floor(Math.random() * this.effects.length)];
        var e2 = this.effects[Math.floor(Math.random() * this.effects.length)];
        var e3 = this.effects[Math.floor(Math.random() * this.effects.length)];
        var o1 = this.offsets[Math.floor(Math.random() * this.offsets.length)];
        var o2 = this.offsets[Math.floor(Math.random() * this.offsets.length)];
        var o3 = this.offsets[Math.floor(Math.random() * this.offsets.length)];
        var anim1 = {
            'opacity': 1
        };
        anim1[e1] = '0px';
        var anim2 = {
            'opacity': 1
        };
        anim2[e2] = '0px';
        var anim3 = {
            'opacity': 1
        };
        anim3[e3] = '0px';
        if (title){
            title.css(e1, o1);
        }
        if (text) {
            text.css(e2, o2);
            buttons.css(e3, o3);
        }

        if (title) {
            title.animate(anim1, 500, function(){
                if (text){
                     text.animate(anim2, 200, function (){
                        if (buttons){
                             buttons.animate(anim3, 300, function (){

                            });
                        }
                    });
                }
            });
        }
    },
    navigate: function(dir){
        if (dir < 0)
            var dirText = 'left';
        else
            var dirText = 'right';
        var ch = this.slidesList.children();
        var slidesNr = ch.length;
        ch.css('display','none');
        this.currentSlide = this.currentSlide + dir;
        if (this.currentSlide > slidesNr - 1)
            this.currentSlide = 0;
        if (this.currentSlide < 0)
            this.currentSlide = slidesNr - 1;

        var me = this;
        me.hideSlideElements();
        $(ch[this.currentSlide]).show('slide', {direction: dirText}, 500,
        function(){
            me.animateSlide();
        });
        //$(ch[this.currentSlide]).css('display','block');
        //this.element.animate({

        //});
    }
});