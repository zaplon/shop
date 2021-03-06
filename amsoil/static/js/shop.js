$(document).ready(function($){

    Handlebars.registerHelper("displayProductAtt", function(name, options) {
      if (name == 'Lepkość')
        return options.fn(this);
      else
        return options.inverse(this);
    });

    $('#accept-cookies').click(function(){
        var me = this;
        $.get('/accept-cookies').success(function(){
            $(me).parent().remove();
        });
    });

    $(window).scroll(function(ev) {
      var y = window.pageYOffset;
      var h = 43;
      var offset = 43 - y;
      if (offset > 0)
        $('header').css('top', offset+'px');
      else
        $('header').css('top', '0px');
    });

    //$('header').css('width',$('#top').width()+'px');

    //footer zawsze na dole strony
//    var minh = $(document).height() - $('footer').height() - $('#top').height() - $('header').height();
//    if ($('.container-fluid').height() < minh)
//        $('.container-fluid').height(minh);
    $('[data-toggle="tooltip"]').tooltip();

    $('#logo').click(function(){
       window.location = '/';
    });

    $('.show-on-click').click(function(){
        if ($(this).is(':checked'))
            $('#'+$(this).attr('data-hide')).css('display','none');
        else
            $('#'+$(this).attr('data-hide')).css('display','block');
    });

    $('div#products').delegate('.product-image','click',function(){
       window.location = '/sklep/produkt/' + $(this).attr('data-product-name') + '/';
    });

    $('.container-fluid').delegate('.variations-table select','change', function(){
        $(this).find('option')[0].setAttribute('disabled',false);
        var pId = $(this).attr('data-product');
        var button = $('button[data-product='+pId+']');
        var div = $('.variations-table[data-product='+$(this).attr('data-product')+']');
        var selectedVariation = shop.getSelectedVariation(div);

        //var amount = $('input.amount[data-variation='+selectedVariation+']').val();
        var product = shop.products.filter(function(p){ if (p.id == pId)  return true })[0];
        var variation = product.variations.filter(function(v){ if (v.id == selectedVariation) return true })[0];
        var amount = variation.amount;

        if (variation.image)
            $('div.product-image[data-product='+pId+']').css('background-image','url("'+variation.image+'")');
        else
            $('div.product-image[data-product='+pId+']').css('background-image','url("'+product.image+'")');

        button.removeClass('hidden');
        if (amount > 0){
            button.removeClass('disabled');
            button.removeClass('btn-primary add-to-cart');
            button.addClass('btn-primary add-to-cart');
            //button.attr('data-variation',selectedVariation);
            button.prop('disabled', false);
            button.html('Do koszyka');
        }
        else {
            button.removeClass('btn-default btn-primary');
            button.addClass('btn-default');
            button.addClass('disabled');
            button.prop('disabled', true);
            button.html('Brak w magazynie');
        }
        var dtls = $('.variations-details[data-product='+$(this).attr('data-product')+']');
     	$(dtls).find('.variation-details').css('display','none');
        $(dtls).find('.price-from').css('display','none');
     	$(dtls).find('.variation-details[data-variation='+selectedVariation+']').css('display','block');
    });


    $('.container-fluid').delegate('.add-to-cart', 'click', function(){
       var id = $(this).attr('data-product');
       var isVariable = $(this).hasClass('variable');
       var hasSingleVariation = $(this).hasClass('single-var');
       if (isVariable && !hasSingleVariation) {
           var pv = shop.getSelectedVariation($('.variations-table[data-product=' + $(this).attr('data-product') + ']'));
           p = shop.products.filter(function(p){ if  (p.id == id) return true  })[0];
           pv = p.variations.filter(function(v){ if (v.id == pv) return true })[0];
       }
       if (hasSingleVariation) {
           pv = shop.products.filter(function(p){ if  (p.id == id) return true  })[0].variations[0];
       }
      if (pv.amount > 0)
        shop.addToCart(pv.id, true);
    });

    $('#account #login').click(function(){
        var password_reset = $('input[name="password-reset"]').val();
        shop.showWindow(tr('Zaloguj'), Mustache.render(Mustache.TEMPLATES['loginForm'], {'password-reset':password_reset} ) );
        $('#doLogin').click(function(){
            $.post('/login/', $('#login-form').serialize(), function(res){
                res = JSON.parse(res);
                if (res.success)
                    window.location.reload();
                else {
                    $('.login-error').css('display','block');
                    $('.login-error').html(res.message);
                }
            });
        });
    });

     $('#account #register').click(function(){
        window.location = '/zarejestruj'
     });

    $('header').delegate('#checkout','click',function(){
        window.location = '/zamowienie';
    });

    $('header').delegate('#cart','click',function(){
        window.location = '/koszyk';
    });

    $('.product-filter .thick-box').click(function(){
       var type = $(this).attr('data-type');
       var id = $(this).attr('data-id');
       if ($(this).hasClass('filter-active')){
           $(this).removeClass('filter-active');
           $(this).removeClass('glyphicon glyphicon-ok');
           delete(shop.filters.attributes[id])
       }
       else {
           $(this).addClass('filter-active');
           $(this).addClass('glyphicon glyphicon-ok');
           shop.filters.attributes[id] = true;
       }
    });

    $('body').delegate('#product-categories .thick-box', 'click', function(){
       if ($(this).hasClass('filter-active')){
           $(this).removeClass('filter-active');
           $(this).removeClass('glyphicon glyphicon-ok');
           delete(shop.filters.categories[$(this).attr('category')]);
       }
       else {
           $(this).addClass('filter-active');
           $(this).addClass('glyphicon glyphicon-ok');
           shop.filters.categories[$(this).attr('category')] = true;
       }
    });


    shop.decorate();

    $('.container-fluid').css('minHeight',($(window).height()-$('#top').height()-$('nav').height()-
        $('header').height() - $('footer').height()-40)+'px');

    //logowanie i rejestracja
    $('.do-login').click(function(){
        $.post('/login/', $('#login-form').serialize(),function(res){
            res = JSON.parse(res);
            if (res.success == false){
                $('.login-error').css('display','block');
                $('.login-error').html(res.message);
            } else
                window.location.reload();
        })
    });

});

shop = {
    currentPage: 1,
    displayAs: 'grid',
    quantity: 1,
    drawElipse: function drawEllipse(context,centerX, centerY, width, height) {

      context.beginPath();
      context.moveTo(centerX - width/2, centerY); // A1

      context.bezierCurveTo(
      centerX - width/2, centerY + height/2, // C1
      centerX + width/2, centerY + height/2, // C2
      centerX + width/2, centerY); // A2

      context.fillStyle = "#999999";
      context.fill();
      context.closePath();
    },
    decorate: function(){
      divs = $('.product-dec canvas, canvas.dec');
      divs.each(function(i,c){
          var w = $(c).parent().parent().width();
          var h = $(c).height();
          c.width = w;
          var context = c.getContext("2d");
          context.shadowOffsetX = 0;
          context.shadowOffsetY = 0;
          context.shadowBlur = 10;
          context.shadowColor = "#222222";
          shop.drawElipse(context,w/2, 0, w-10, h-5);
      });
    },
    showMessage: function(message, icon){
        $('#decorative-message').remove();
        $('body').append('<div id="decorative-message"><div class="icon"></div><div class="message"><span></span></div></div>');
        var div = $('#decorative-message');
        $('#decorative-message .message span').html(message);
        $('#decorative-message .icon').addClass(icon);
        div.animate({ opacity:'1'},500, function(){
            window.setTimeout(function(){
                div.animate({opacity:'0'},500, function(){
                    div.remove();
                });
            },2000)}
        );
    },
    showTopMessage: function(message){
        $('#top-message').html(message);

        $('#top-message').animate({padding:'15px',borderWidth:'2px'},200);
        window.setTimeout(function(){
            $('#top-message').animate({padding:'0px',borderWidth:'0px'},200);
            $('#top-message').html('');
        },2000);

//        $('#top-message').animate({padding:'15px',borderWidth:'2px'},200);
//        window.setTimeout(function(){
//            $('#top-message').animate({padding:'0px',borderWidth:'0px'},200);
//            $('#top-message').html('');
//        },2000);
    },
    showWindow: function(title,body,footer,buttons){

        $('.modal-dialog').remove();

        var id = new Date().getTime();
        var w = '<div class="modal-dialog" id="'+id+'">';
        w = w + '<div class="modal-content">';
        w = w + '<div class="modal-header">';
        w = w + '<button type="button" class="close" data-dismiss="modal"><span aria-hidden="true">&times;</span><span class="sr-only">Close</span></button>';
        w = w + '<h4>' + title + '</h4></div>';
        w = w + '<div class="modal-body">' + body + '</div>';
        w = w + '</div></div>';
        var b = $('body');
        b.append(w);
        var d = $('#'+id);
        d.css('top', parseInt($(window).height()/2 - d.height()/2)+'px');
        d.css('left', parseInt($(window).width()/2 - d.width()/2 )+'px');
        $('#'+id + ' .close').click(function(){
           $(this).parent().parent().remove();
        });
        //d.draggable();
    },
    login: function(){
    },
    register: function(){

    },
    addToCart: function(id, variable){
        var data = variable ? { 'productVariation': id } : { 'product': id};
        data.quantity = shop.quantity;
        $.ajax({
            url: '/addToCart/',
            method: 'POST',
            data: data,
            success: function (res) {
                if (res.success == false){
                    shop.showMessage(tr(res.message), 'glyphicon glyphicon-remove');
                }
                else {
                    $.get('/miniCart', {}, function (res) {
                        $('#mini-cart').html(Mustache.to_html(Mustache.TEMPLATES.miniCart,
                            JSON.parse(res)));
                        //shop.showTopMessage(tr('Product added to cart'));
                        shop.showMessage(tr('Produkt dodany do koszyka'), 'glyphicon glyphicon-shopping-cart');
                    });
                }
            }
        });
    },
    filters: {
        categories: {},
        attributes: {},
        onlyCategories: '',
        onlyAttributes: '',
        sortBy: 'name'
    },
    getSelectedVariation: function(div){
        
    	var selects = $(div).find('select');
        var variations = [];
        selects.each(function(ind,el){
    	    var opt = $(el).find(':selected');
                variations.push($(opt).attr('data-variations').split(','));
        });
        var cands = variations[0];
        if (cands.length > 1)
            variations.forEach(function(v){
                cands.forEach(function(c,ind){
                    if (v.indexOf(c) == -1)
                        cands.remove(c);
                });
            });

        return cands[0];

    },
    mask: function(type){
        var cont = $('.page-container');
        var mask = $('#mask');
        if (type == 1){
            mask.css('height', cont.height()+'px');
            mask.css('display','block');
        }
        else 
            mask.css('display','none');
    },
    getProducts: function(container){
        var filters = '';
        var cats = [];
        var atts = [];
        var page = 1;
        for (f in this.filters.categories)
            cats.push(f);
        cats = cats.join(',');
        for (f in this.filters.attributes)
            atts.push(f);
        atts = atts.join(',');
        filters = filters + 'page=' + shop.currentPage + '&';
        filters = filters + 'categories_in=' + cats;
        filters = filters + '&attributes_in=' + atts;

        //stałe parametry
        filters = filters + '&category__id=' + this.filters.onlyCategories;
        filters = filters + '&attributes__id=' + this.filters.onlyAttributes;

        if ($('#price-filter').attr('data')){
            var p = $('#price-filter').attr('data').split(':')[1];
            filters = filters + '&price_in=' + p.substr(2,p.length-3);
        }
        filters = filters + '&o=' + shop.filters.sortBy;
        $.get('/api/products?' + filters).done(function(res){
           var cont = $('#'+container)[0];
           $('.product').remove();
           $('#no-products').remove();

          //brak productów
          if (res.count == 0){
              $(cont).html('<div id="no-products"><h3>Brak produktów</h3></div>');
              $('#shop-pagination').children().remove();
              return;
          }

          //numeracja stron
          var pagination = $('#shop-pagination');
          pagination.children().remove();
          if (shop.currentPage == 1) {}
           // pagination.append('<li data-page='+(shop.currentPage-1)+' class="disabled"><a href="#"><span aria-hidden="true">&laquo;</span><span class="sr-only">Previous</span></a></li>');
          else
            pagination.append('<li data-page='+(shop.currentPage-1)+' class="enabled"><a href="#"><span aria-hidden="true">&laquo;</span><span class="sr-only">Previous</span></a></li>');
          for(var i=0;i<res.count/10;i++)
            pagination.append('<li data-page='+(i+1)+' class="enabled"><a href="#">'+(i+1)+' <span class="sr-only">(current)</span></a></li>');
          if (shop.currentPage == i) {}
          //  pagination.append('<li data-page='+(shop.currentPage+1)+' class="disabled"><a href="#"><span aria-hidden="true">&raquo;</span><span class="sr-only">Previous</span></a></li>');
          else
            pagination.append('<li data-page='+(shop.currentPage+1)+' class="enabled"><a href="#"><span aria-hidden="true">&raquo;</span><span class="sr-only">Previous</span></a></li>');
          var aPage = $('li[data-page="'+shop.currentPage+ '"]');//pagination.children()[shop.currentPage];
          //$(aPage).removeClass('disabled');
          $('#shop-pagination li').click(function(){
             shop.currentPage = parseInt($(this).attr('data-page'));
             shop.getProducts('products');
          });

          $(aPage).addClass('active');

          shop.products = res.results;
          for (r in res.results) {

               res.results[r].min_price = res.results[r].min_price.toFixed(2).replace('.',',');
               res.results[r].variations.forEach(function(v){
                   v.price = v.price.toFixed(2).replace('.',',');
               });

               if ((r) % 3 == 0)
                $(cont).append('<div style="clear:both"></div>');
               var div = document.createElement('div');
               if (shop.displayAs == 'grid')
                div.className = 'product product-grid col-md-4 col-sm-12';
               else
                div.className = 'product product-list col-md-12 col-sm-12';
               cont.appendChild(div);

               if (res.results[r].variations.length == 0)
                res.results[r].noVars = true;
               else
                res.results[r].noVars = false;

               p = res.results[r];
               //p.grouped_variations = JSON.parse(p.grouped_variations.replace(/'/g, '"'));

               if (shop.displayAs == 'grid') {
                   $(div).html(Handlebars.templates['productSmall']( {'addToCart': 'Do koszyka', 'product': p }));
                   //$(div).html(Mustache.to_html(Mustache.TEMPLATES.productSmall, {'addToCart': 'Do koszyka', 'product': res.results[r] }));
               }
               else {
                   $(div).html(Handlebars.templates['product']({'addToCart': 'Do koszyka', 'product': p }));
                   //$(div).html(Mustache.to_html(Mustache.TEMPLATES.product, { 'addToCart':'Do koszyka', 'product': res.results[r] }));
               }
           }
           shop.decorate();
        });
    }
}


// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        shop.mask(1);
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    },
    complete: function(){
        shop.mask(-1);
    }
});


function tr(str){
    return str;
}