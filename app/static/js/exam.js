Vue.use(Toasted, {
    iconPack : 'fontawesome'
})

var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Exam Center',
        landed: false,
        
        students: [],
        branches: [],
        categories: [],
        subjects: [{id:1, name:'English'}, {id:2, name:'Hindi'}, {id:3, name:'Maths'}],

        error: '',
        message: '',
        loading: 'Loading ...',
    },
    created: function(){
        this.load(['students', 'branches', 'categories'],this.after)
    },
    updated: function(){
        console.log('updated')
        var dom = $(this.$el)
        dom.find('#afterLanding').show()
        dom.find('.ui.dropdown').dropdown()
        this.landed = true
    },
    methods: {
        after: function(){
            this.heading = 'Exam Center'
        }
    }
})