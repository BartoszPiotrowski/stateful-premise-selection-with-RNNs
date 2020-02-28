:- use_module(library(assoc)).
:- use_module(library(ordsets)).
:- use_module(library(readutil)).

declare_TPTP_operators1:-
    op(99,fx,'$'),
    op(100,fx,++),
    op(100,fx,--),
    op(100,xf,'!'),
    op(400,fx,'^'),
    op(405,xfx,'='),
    op(405,xfx,'~='),
    op(450,fy,~),
    op(501,yfx,'@'),
    (system_mode(true),op(502,xfy,'|'),system_mode(false)),
    op(502,xfy,'~|'),
    op(503,xfy,&),
    op(503,xfy,~&),
    op(504,xfy,=>),
    op(504,xfy,<=),
    op(505,xfy,<=>),
    op(505,xfy,<~>),
%----! and ? are of higher precedence than : so !X:p(X) is :(!(X),p(X))
%----Otherwise !X:!Y:p(X,Y) cannot be parsed.
    op(400,fx,!),
    op(400,fx,?),
%----Need : stronger than + for equality and otter in tptp2X
%----Need : weaker than quantifiers for !X : ~p
    op(450,xfy,:),
%---- .. used for range in tptp2X. Needs to be stronger than :
    op(400,xfx,'..').



%%%%%%%%% features by walks and truncated subterms %%%%
%% ## TEST: :- declare_mptp_predicates,load_mml,install_index,tell(foo6708),time((fof(A,B,C,D,E),bag_of_walks_top(C,Res,P),write(A),write(P),nl,fail)).
% 894,737,797 inferences, 68.100 CPU in 68.789 seconds (99% CPU, 13138587 Lips)

%% enigma_features(+Formula,-Assoc,-Pairs)
enigma_features(X,Assoc,Pairs):- bag_of_walks_top(X,Assoc,Pairs).
	
bag_of_walks_top(X,Res,Pairs) :- !,
	copy_term(X,X1),
	numbervars(X1,1000,_),
	empty_assoc(Assoc),
	bag_of_walks(X1,Assoc,Res),
	assoc_to_list(Res, Pairs).

bag_of_walks_l([],In,In).
bag_of_walks_l([H|T],In,Out):-
	bag_of_walks(H,In,S1),
	bag_of_walks_l(T,S1,Out).

bag_of_walks(X,In,Out):-
	X =.. [F|Args],
	term_hash(F,4,262139,F1),
	bag_insert(F1,In,In0),
	add_tuples_to_bag(F,Args,In0,In1),
	bag_of_walks_l(Args, In1, Out).

%% add_tuples_to_bag(+F,+Args,+In,-Out)

add_tuples_to_bag(_,[],In,In).
add_tuples_to_bag(F,[H|T],In,Out):-
	H =.. [H1|T1],
	X =.. [F|[H1]],
	%% possibly call term_hash on X here?
	term_hash(X,4,262139,X1),
	bag_insert(X1,In,Out1),
	add_triples_to_bag(F,H1,T1,Out1,Out2),
	add_tuples_to_bag(F,T,Out2,Out).

add_triples_to_bag(_,_,[],In,In).
add_triples_to_bag(F,H1,[H|T],In,Out):-
	H =.. [H2|_],
	X =.. [F|[H1,H2]],
	%% possibly call term_hash on X here?
	term_hash(X,4,262139,X1),
	bag_insert(X1,In,Out1),
	add_triples_to_bag(F,H1,T,Out1,Out).

bag_insert(X,In,Out):-
	(get_assoc(X, In, V) ->
	 V1 is V + 1
	;
	 V1 is 1
	 ),
	put_assoc(X, In, V1, Out).

bag_insert_l([],In,In).
bag_insert_l([H|T],In,Out):-
	bag_insert(H,In,Out1),
	bag_insert_l(T,Out1,Out).
	
bag_of_terms_top(X,Res) :- !,
	copy_term(X,X1),
	numbervars(X1,0,_),
	empty_assoc(Assoc),
	bag_of_terms(X1,Assoc,Res).

bag_of_terms_l([],In,In).
bag_of_terms_l([H|T],In,Out):-
	bag_of_terms(H,In,S1),
	bag_of_terms_l(T,S1,Out).

bag_of_terms($true,In,In):- !.
bag_of_terms(X,In,Out):-
	X =.. [F|Args],
	bag_insert_l([X,F],In,In1),
	bag_of_terms_l(Args, In1, Out).
