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

        branch: {},
        studentCatFilter: '',

        error: '',
        message: '',
        loading: 'Loading ...',
    },
    created: function(){
        this.loadv2([
        {
            name:'Branches',
            url:'/api/branch/list',
            variableName: 'branches',
            dataInReponse: 'branches'
        }
        ], this.after)
    },
    updated: function(){
        console.log('updated')
        var dom = $(this.$el)
        dom.find('#afterLanding').show()
        dom.find('.ui.dropdown').dropdown()
        this.landed = true
    },
    watch: {
        branch: function(){
            this.loadv2([
            {
                name:'Students',
                url:'/api/student/'+this.branch.id+'/list',
                variableName: 'students',
                dataInReponse: 'students'
            },
            {
                name:'Categories',
                url:'/api/category/'+this.branch.id+'/list',
                variableName: 'categories',
                dataInReponse: 'categories'
            },
            {
                name:'Exams',
                url:'/api/exam/'+this.branch.id+'/list',
                variableName: 'exams',
                dataInReponse: 'exams'
            },
            {
                name:'Subjects',
                url:'/api/subject/'+this.branch.id+'/list',
                variableName: 'subjects',
                dataInReponse: 'subjects'
            },
            ])
        }
    },
    computed: {
        filteredStudents: function(){
            return this.students.filter((std) => {
                return std.category === this.studentCatFilter
            })
        },
    },
    methods: {
        after: function(){
            this.heading = 'Exam Center'
            this.branches.forEach(branch=>{
                if(branch.id===this.branchId)
                    this.branch = branch
            })
        },
        onBranchChange: function(){
            var data = $('#branchForm').form('get values')
            var selectedBranchId = parseInt(data.branch)
            var index = -1
            this.branches.forEach((branch, i) => {
                if(branch.id === selectedBranchId){
                    index = i
                }
            })
            if(index != -1){
                this.branch = this.branches[index]
            }
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