$.widget( "geekman.productSlider", {
    _create: function() {
        this.slidesList = this.element.find('.product-tab-item');
        this.arrowLeft = this.element.find('.slide-left');
        this.arrowRight = this.element.find('.slide-right');
        this.slidesNr = this.slidesList.length;
        this.step = 1;
        this.offset = 0;
        this.visible = 4;

        var me = this;

        this.arrowLeft.click(function () {
            me.navigate(-1);
        });
        this.arrowRight.click(function () {
            me.navigate(1);
        });
        this.navigate(0);
    },
    navigate: function(dir){
        this.offset += this.step*dir;
        var me = this;
        this.slidesList.css('display','none');

           this.slidesList.each(function(el,s){
              nr = parseInt($(s).attr('data-nr'));
              new_nr = nr + me.step*dir;
              if (new_nr > 0 && new_nr <= me.slidesNr)
                $(s).attr('data-nr',parseInt(new_nr));
              else if (new_nr == 0)
                $(s).attr('data-nr',me.slidesNr);
              else
                $(s).attr('data-nr',1);
           });

        var slides = this.slidesList.detach().sort(function(a, b) {
           return $(a).attr('data-nr') > $(b).attr('data-nr');
        });

        this.element.find('.products-container').append(slides);

        if (this.offset < 0) {
            this.offset = this.slidesNr;
        }
        if (this.offset > this.slidesNr) {
            this.offset = 0;
        }

        slides.filter( function(){ return $(this).attr('data-nr') <= me.visible } ).css('display','inline-block');

    }
})