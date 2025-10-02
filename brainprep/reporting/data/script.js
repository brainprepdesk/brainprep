
/**
 * Menu handling.
 */
$(function() {

  var siteSticky = function() {
		$(".js-sticky-header").sticky({topSpacing:0});
	};
	siteSticky();

	var siteMenuClone = function() {

		$('.js-clone-nav').each(function() {
			var $this = $(this);
			$this.clone().attr('class', 'site-nav-wrap').appendTo('.site-mobile-menu-body');
		});


		setTimeout(function() {
			
			var counter = 0;
      $('.site-mobile-menu .has-children').each(function(){
        var $this = $(this);
        
        $this.prepend('<span class="arrow-collapse collapsed">');

        $this.find('.arrow-collapse').attr({
          'data-toggle' : 'collapse',
          'data-target' : '#collapseItem' + counter,
        });

        $this.find('> ul').attr({
          'class' : 'collapse',
          'id' : 'collapseItem' + counter,
        });

        counter++;

      });

    }, 1000);

		$('body').on('click', '.arrow-collapse', function(e) {
      var $this = $(this);
      if ( $this.closest('li').find('.collapse').hasClass('show') ) {
        $this.removeClass('active');
      } else {
        $this.addClass('active');
      }
      e.preventDefault();  
      
    });

		$(window).resize(function() {
			var $this = $(this),
				w = $this.width();

			if ( w > 768 ) {
				if ( $('body').hasClass('offcanvas-menu') ) {
					$('body').removeClass('offcanvas-menu');
				}
			}
		})

		$('body').on('click', '.js-menu-toggle', function(e) {
			var $this = $(this);
			e.preventDefault();

			if ( $('body').hasClass('offcanvas-menu') ) {
				$('body').removeClass('offcanvas-menu');
				$this.removeClass('active');
			} else {
				$('body').addClass('offcanvas-menu');
				$this.addClass('active');
			}
		}) 

		// click outisde offcanvas
		$(document).mouseup(function(e) {
	    var container = $(".site-mobile-menu");
	    if (!container.is(e.target) && container.has(e.target).length === 0) {
	      if ( $('body').hasClass('offcanvas-menu') ) {
					$('body').removeClass('offcanvas-menu');
				}
	    }
		});
	}; 
	siteMenuClone();

});



/**
 * A class representing a carousel that cycles through different objects.
 */
class Carousel {
    /**
     * Creates a new Carousel instance.
     * @param {string} uid - A unique identifier for the masker report.
     * @param {number[]} displayed_objects - An array of IDs to cycle through.
     */
    constructor(uid, displayed_objects) {
        /** @private {string} */
        this.uid = uid;
        console.log("uid=" + this.uid);

        /** @private {number[]} */
        this.displayed_objects = displayed_objects;
        console.log("names=" + this.displayed_objects);

        /** @private {number} */
        this.current_obj_idx = 0;
        console.log("new index=" + this.current_obj_idx);

        /** @private {number} */
        this.number_objs = displayed_objects.length;
        console.log("size=" + this.number_objs);

        this.init();
    }

    /**
     * Initializes the carousel by setting up event listeners and displaying the first object.
     */
    init() {
        this.showObj(this.current_obj_idx);

        let prevButton = document.querySelector(`#prev-btn-${this.uid}`);
        let nextButton = document.querySelector(`#next-btn-${this.uid}`);

        if (prevButton) prevButton.addEventListener("click", () => this.displayPrevious());
        if (nextButton) nextButton.addEventListener("click", () => this.displayNext());

        this.bindKeyboardEvents();
    }

    /**
     * Displays the object at the given index and hides all others.
     * @param {number} index - The index of the map to display.
     *
     * for sphere masker report this adapts the full title in the carousel
     */
    showObj(index) {
        this.displayed_objects.forEach((_, i) => {
            let mapElement = document.getElementById(`carousel-obj-${this.uid}-${i}`);
            if (mapElement) {
                mapElement.style.display = i === index ? "block" : "none";
            }
        });

        let compElement = document.getElementById(`comp-${this.uid}`);
        if (compElement) {
            compElement.innerHTML = this.displayed_objects[index];
        }
    }

    /**
     * Advances the carousel to the next object.
     *
     * using % modulo to ensure we 'wrap' back to start in the carousel
    */
    displayNext() {
        this.current_obj_idx = (this.current_obj_idx + 1) % this.number_objs;
        console.log("new index=" + this.current_obj_idx);
        this.showObj(this.current_obj_idx);
    }

    /**
     * Moves the carousel to the previous object.
     *
     * using % modulo to ensure we 'wrap' back to start in the carousel
    */
    displayPrevious() {
        this.current_obj_idx = (this.current_obj_idx - 1 + this.number_objs) % this.number_objs;
        console.log("new index=" + this.current_obj_idx);
        this.showObj(this.current_obj_idx);
    }

    /**
     * Binds carousel to right and left arrow keys to cycle through carousel.
    */
    bindKeyboardEvents() {
        document.addEventListener("keydown", (event) => {
            if (event.key === "ArrowRight") {
                this.displayNext();
            } else if (event.key === "ArrowLeft") {
                this.displayPrevious();
            }
        });
    }
}   
