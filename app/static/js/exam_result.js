var app = new Vue({
    mixins: [utils],
    el: '#app',
    data:{
        landed: false,
        loading: '',
        error: '',
        message: '',

        me: undefined,
        branches: [],
        exams: [],
        subjects: [],
        students: [],
        categories: [],
        grades: [],
        faculties: [],

        selectedBranch: undefined,
        selectedExam: undefined,
    },
    created: function(){
        this.loadv2([
        {
            name:'Branches',
            url:'/api/branch/list',
            variableName: 'branches',
            dataInReponse: 'branches'
        },
        {
            name: 'Me',
            url: '/api/myprofile',
            variableName: 'me',
            dataInReponse: 'me'
        }
        ], this.init)
    },
    updated: function(){
        console.log('updated')
    },
    watch: {
        selectedBranch: function(){
            this.loadv2([{
                name:'Exams',
                url:'/api/exam/'+this.selectedBranch.id+'/list',
                variableName: 'exams',
                dataInReponse: 'exams'
            },
            {
                name:'Categories',
                url:'/api/category/'+this.selectedBranch.id+'/list',
                variableName: 'categories',
                dataInReponse: 'categories'
            },
            {
                name:'Exams',
                url:'/api/exam/'+this.selectedBranch.id+'/list',
                variableName: 'exams',
                dataInReponse: 'exams'
            },
            {
                name:'Grades',
                url:'/api/grade/'+this.selectedBranch.id+'/list',
                variableName: 'gradeRules',
                dataInReponse: 'grades'
            }
            ])
        },
        selectedExam: function(){
            this.loadv2([
            {
                name:'Students',
                url:'/api/student/'+this.selectedBranch.id+'/list',
                variableName: 'students',
                dataInReponse: 'students'
            },
            {
                name:'Subjects',
                url:'/api/subject/'+this.selectedBranch.id+'/list',
                variableName: 'subjects',
                dataInReponse: 'subjects'
            },
            ])
        }
    },
    computed: {
    },
    methods: {
        init: function(){
            this.branches.forEach(branch => {
                if(branch.id === this.branchId)
                    this.branch = branch
            })
            var dom = $(this.$el)
            dom.find('#afterLanding').show()
            dom.find('.ui.dropdown').dropdown()
            this.landed = true
        },
        onBranchChange: function(){
            var branchId = $('#branchDropDown').dropdown('get value')
            var branchId = parseInt(branchId)
            var index = -1
            this.branches.forEach((branch, i) => {
                if(branch.id === branchId){
                    index = i
                }
            })
            if(index != -1){
                this.selectedBranch = this.branches[index]
            }
        },
        onExamChange: function(){
            var examId = $('#examDropDown').dropdown('get value')
            var examId = parseInt(examId)
            var index = -1
            this.exams.forEach((exam, i) => {
                if(exam.id === examId){
                    index = i
                }
            })
            if(index != -1){
                this.selectedExam = this.exams[index]
            }
        },
    }
})