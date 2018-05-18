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
        this.landed = true
    },
    methods: {
        after: function(){
            this.heading = 'Under Construction'
        }
    }
})