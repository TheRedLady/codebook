function QuestionListItemViewModel(data) {
    var self = this;
    self.questionId = data['id'];
    self.questionUrl = data['url'];
    self.title = data['title'];
    self.author = new AuthorViewModel(data['author']);
    self.votes = data['votes'];
    self.content = data['content'];
    self.datePublished = data['created'];
    self.tags = data['tags'].map(function(tag) {
        return new TagViewModel(tag);
    });
    self.isPopular = data['is_popular'];

    self.remove = remove;

    //----

    function remove() {
        $.ajax({
            url: RESTAPI_URLS.QUESTIONS + self.questionId + '/',
            method: METHODS.DELETE,
        });
    }

    return self;
};

function QuestionListViewModel(params) {
    var self = this;
    self.page = params.page;
    self.tag = params.tag;
    self.questions = ko.observableArray([]);

    init();

    //--------

    function init() {
        var url = '';
        if (self.tag) {
            url += RESTAPI_URLS.TAGS + self.tag + TAG_PAGES.QUESTIONS;
        } else {
            url += RESTAPI_URLS.QUESTIONS + self.page;
        }
        $.ajax({
            url: url,
            type: METHODS.GET
        }).done(function(data) {
            data.forEach(function(question) {
                self.questions.push(new QuestionListItemViewModel(question));
            });
        });

    }

};

ko.components.register('questions-list-component', {
    template: { element: 'questions-list-template' },
    viewModel: QuestionListViewModel
});
