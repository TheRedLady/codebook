function QuestionViewModel(params) {
    var self = this;
    self.userId = params.user_id;
    self.questionId = params.id;
    self.title = ko.observable('');
    self.author = ko.observable({});
    self.votes = ko.observable(0);
    self.content = ko.observable('');
    self.datePublished = ko.observable('');
    self.voted = ko.observable(null);
    self.tags = ko.observableArray([]);
    self.isPopular = ko.observable(false);
    self.answers = ko.observableArray([]);

    self.upvote = upvote;
    self.downvote = downvote;
    self.addAnswer = addAnswer;
    self.removeAnswer = removeAnswer;

    init();

    //------------

    function init() {
        $.ajax({
            url: RESTAPI_URLS.QUESTIONS + self.questionId + '/',
            type: METHODS.GET
        }).done(function(data) {
            self.title(data['title']);
            self.author(new AuthorViewModel(data['author']));
            self.content(data['content']);
            self.votes(data['votes']);
            self.datePublished(data['created']);
            self.isPopular(data['is_popular']);
            data['tags'].forEach(function(tag) {
                self.tags.push(new TagViewModel(tag));
            });
        });

        $.ajax({
            url: RESTAPI_URLS.QUESTIONS + self.questionId + '/answers/',
            type: METHODS.GET
        }).done(function(data) {
            data.forEach(function(answer) {
                self.answers.push(new AnswerViewModel(answer));
            });
        });

        $.ajax({
            url: RESTAPI_URLS.QUESTIONS + self.questionId + RESTAPI_URLS.VOTE,
            method: METHODS.GET,
        }).done(function(data) {
            self.voted(data['vote'] || null);
        });
    }

    function upvote() {
        var url = RESTAPI_URLS.QUESTIONS + self.questionId + RESTAPI_URLS.UPVOTE;
        $.ajax({
            url: url,
            method: METHODS.POST,
        }).done(function(data) {
            self.votes(data['total_votes']);
            self.voted('up');
        });
    }

    function downvote() {
        var url = RESTAPI_URLS.QUESTIONS + self.questionId + RESTAPI_URLS.DOWNVOTE;
        $.ajax({
            url: url,
            method: METHODS.POST,
        }).done(function(data) {
            self.votes(data['total_votes']);
            self.voted('down');
        });
    }

    function remove() {
        $.ajax({
            url: RESTAPI_URLS.QUESTIONS + self.questionId + '/',
            method: METHODS.DELETE,
        });
    }

    function addAnswer() {
        if (!self.newAnswerContent()) {
            return;
        }
        $.ajax({
            url: RESTAPI_URLS.ANSWERS,
            data: {
                'author': self.userId,
                'content': self.newAnswerContent(),
                'question': self.questionId,
            },
            method: METHODS.POST,
        }).done(function(data) {
            $.ajax({
                url: RESTAPI_URLS.ANSWERS + data['id'] + '/',
                method: METHODS.GET,
            }).done(function(data){
                self.newAnswerContent('');
                self.answers.push(new AnswerViewModel(data));
            });
        });
    }

    function removeAnswer(answer) {
        answer.remove();
        self.answers.remove(answer);
    }
};


ko.components.register('question-component', {
    template: { element: 'question-template' },
    viewModel: QuestionViewModel
});


