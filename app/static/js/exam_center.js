var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        heading: 'Exam Center',
        landed: false,
        
        students: [],
        branches: [],
        categories: [],
        exams: [],
        subjects: [],
        marks: [],

        tests: [],

        studentCatFilter: '',

        error: '',
        message: '',
        loading: 'Loading ...',
    },
    created: function(){
        this.loadv2([
            {name:'Students',
             url:'/api/student/1/list',
             variableName: 'students',
             dataInReponse: 'students'},
            {name:'Categories',
             url:'/api/category/1/list',
             variableName: 'categories',
             dataInReponse: 'categories'},
            {name:'Exams',
             url:'/api/exam/1/list',
             variableName: 'exams',
             dataInReponse: 'exams'},
            {name:'Subjects',
             url:'/api/subject/1/list',
             variableName: 'subjects',
             dataInReponse: 'subjects'}
             ], this.after)
    },
    updated: function(){
        console.log('updated')
        var dom = $(this.$el)
        dom.find('#afterLanding').show()
        dom.find('.ui.dropdown').dropdown()
        this.landed = true
    },
    computed: {
        filteredStudents: function(){
            return this.students.filter((std) => {
                return std.category === this.studentCatFilter
            })
        }
    },
    methods: {
        after: function(){
            this.heading = 'Exam Center'
        },
        onExamChange: function(){
            var data = $('#testCodeForm').form('get values')
            var selectedExamId = parseInt(data.exam)
            var index = -1
            this.exams.forEach((exam, i) => {
                if(exam.id === selectedExamId){
                    index = i
                }
            })
            if(index != -1){
                
                this.tests = this.exams[index].tests
                // if(!testToAdd)
                //     return
                // testsToAdd.forEach((test, i) => {
                //     this.tests.push(test)
                // })
            }
        },
        onTestChange: function(){
            var data = $('#testCodeForm').form('get values')
            var selectedTestId = parseInt(data.test)
            var test = undefined
            this.tests.forEach((t, i)=>{
                if(t.id===selectedTestId){
                    test = t
                }
            })
            if(!test)
                return
            this.studentCatFilter = test.category
        }
    }
})