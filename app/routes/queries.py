from flask import Blueprint, render_template, request
from app.database import Database

queries_bp = Blueprint("query", __name__)


@queries_bp.route("/list_tables")
def list_tables():
    """List all tables in the database."""

    # >>>> TODO 1: Write a query to list all the tables in the database. <<<<

    query = """SHOW Tables;"""

    with Database() as db:
        tables = db.execute(query)
    return render_template("list_tables.html", tables=tables)


@queries_bp.route("/search_movie", methods=["POST"])
def search_movie():
    """Search for movies by name."""
    movie_name = request.form["movie_name"]

    # >>>> TODO 2: Search Motion Picture by Motion picture name. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """SELECT mp.name, mp.rating, mp.production, mp.budget from MotionPicture mp JOIN Movie m ON m.mpid = mp.id WHERE name LIKE %s;"""
    
    with Database() as db:
        movies = db.execute(query, (f"%{movie_name}%",))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_liked_movies", methods=["POST"])
def search_liked_movies():
    """Search for movies liked by a specific user."""
    user_email = request.form["user_email"]

    # >>>> TODO 3: Find the movies that have been liked by a specific user’s email. <<<<
    #              List the movie `name`, `rating`, `production` and `budget`.

    query = """
                SELECT mp.name, mp.rating, mp.production, mp.budget 
                FROM MotionPicture mp INNER JOIN 
                (SELECT m.mpid FROM Movie m INNER JOIN Likes l ON m.mpid = l.mpid WHERE l.uemail = %s) sq ON mp.id = sq.mpid;
            """

    with Database() as db:
        movies = db.execute(query, (user_email,))
    return render_template("search_results.html", movies=movies)


@queries_bp.route("/search_by_country", methods=["POST"])
def search_by_country():
    """Search for movies by country using the Location table."""
    country = request.form["country"]

    # >>>> TODO 4: Search motion pictures by their shooting location country. <<<<
    #              List only the motion picture names without any duplicates.

    query = """SELECT DISTINCT mp.name FROM MotionPicture mp INNER JOIN Location l ON mp.id = l.mpid WHERE l.country = %s;"""

    with Database() as db:
        movies = db.execute(query, (country,))
    return render_template("search_results_by_country.html", movies=movies)


@queries_bp.route("/search_directors_by_zip", methods=["POST"])
def search_directors_by_zip():
    """Search for directors and the series they directed by zip code."""
    zip_code = request.form["zip_code"]

    # >>>> TODO 5: List all directors who have directed TV series shot in a specific zip code. <<<<
    #              List the director name and TV series name only without duplicates.

    query = """SELECT DISTINCT p.name, mp.name
            FROM People p
            JOIN Role r ON p.id = r.pid
            JOIN Series s ON r.mpid = s.mpid
            JOIN MotionPicture mp ON s.mpid = mp.id
            JOIN Location l ON mp.id = l.mpid
            WHERE r.role_name = 'Director'
            AND l.zip = %s;
            """

    with Database() as db:
        results = db.execute(query, (zip_code,))
    return render_template("search_directors_results.html", results=results)


@queries_bp.route("/search_awards", methods=["POST"])
def search_awards():
    """Search for award records where the award count is greater than `k`."""
    k = int(request.form["k"])

    # >>>> TODO 6: Find the people who have received more than “k” awards for a single motion picture in the same year. <<<<
    #              List the person `name`, `motion picture name`, `award year` and `award count`.

    query = """SELECT p.name, m.name, a.award_year, a.award_count
                FROM MotionPicture m 
                JOIN (SELECT COUNT(*) AS 'award_count', mpid, pid, award_year 
                FROM Award GROUP BY mpid, pid, award_year) a ON m.id = a.mpid
                JOIN People p ON a.pid = p.id
                WHERE a.award_count > %s;
                """

    with Database() as db:
        results = db.execute(query, (k,))
    return render_template("search_awards_results.html", results=results)


@queries_bp.route("/find_youngest_oldest_actors", methods=["GET"])
def find_youngest_oldest_actors():
    """
    Find the youngest and oldest actors based on the difference 
    between the award year and their date of birth.
    """

    # >>>> TODO 7: Find the youngest and oldest actors to win at least one award. <<<<
    #              List the actor names and their age (at the time they received the award). 
    #              The age should be computed from the person’s date of birth to the award winning year only. 
    #              In case of a tie, list all of them.

    query = """WITH AwardedAges AS (
                SELECT p.name, a.award_year - YEAR(p.dob) AS age_awarded
                FROM People p
                JOIN Role r ON p.id = r.pid
                JOIN Award a ON p.id = a.pid
                WHERE r.role_name = 'Actor'),
                MinMax AS (
                SELECT MIN(age_awarded) AS min_age, MAX(age_awarded) AS max_age
                FROM AwardedAges)
                SELECT x.name, x.age_awarded
                FROM AwardedAges x
                JOIN MinMax mm 
                ON x.age_awarded = mm.min_age OR x.age_awarded = mm.max_age;
                """

    with Database() as db:
        actors = db.execute(query)
    
    # Filter out actors with null ages (if any)
    actors = [actor for actor in actors if actor[1] is not None]
    if actors:
        min_age = min(actors, key=lambda x: x[1])[1]
        max_age = max(actors, key=lambda x: x[1])[1]
        youngest_actors = [actor for actor in actors if actor[1] == min_age]
        oldest_actors = [actor for actor in actors if actor[1] == max_age]
        return render_template(
            "actors_by_age.html",
            youngest_actors=youngest_actors,
            oldest_actors=oldest_actors,
        )
    else:
        return render_template(
            "actors_by_age.html", youngest_actors=[], oldest_actors=[]
        )


@queries_bp.route("/search_producers", methods=["POST"])
def search_producers():
    """
    Search for American producers based on a minimum box office collection and maximum budget.
    """
    box_office_min = float(request.form["box_office_min"])
    budget_max = float(request.form["budget_max"])

    # >>>> TODO 8: Find the American [USA] Producers who had a box office collection of more than or equal to “X” with a budget less than or equal to “Y”. <<<< 
    #              List the producer `name`, `movie name`, `box office collection` and `budget`.

    query = """SELECT p.name, mp.name,  m.boxoffice_collection, mp.budget
                FROM MotionPicture mp 
                JOIN Movie m ON mp.id = m.mpid
                JOIN Role r ON m.mpid = r.mpid
                JOIN People p ON r.pid = p.id
                WHERE p.nationality = 'USA' AND r.role_name = 'Producer' AND m.boxoffice_collection >= %s AND mp.budget <= %s;"""

    with Database() as db:
        results = db.execute(query, (box_office_min, budget_max))
    return render_template("search_producers_results.html", results=results)


@queries_bp.route("/search_multiple_roles", methods=["POST"])
def search_multiple_roles():
    """
    Search for people who have multiple roles in movies with a rating above a given threshold.
    """
    rating_threshold = float(request.form["rating_threshold"])

    # >>>> TODO 9: List the people who have played multiple roles in a motion picture where the rating is more than “X”. <<<<
    #              List the person’s `name`, `motion picture name` and `count of number of roles` for that particular motion picture.

    query = """  
                SELECT p.name AS Person_Name, m.name AS Motion_Picture_Name, COUNT(r.role_name) AS Role_Number
                FROM Role r
                JOIN MotionPicture m ON m.id = r.mpid 
                JOIN People p ON p.id = r.pid
                WHERE m.rating > %s
                GROUP BY m.id, p.id
                HAVING COUNT(r.role_name) > 1
                ORDER BY Role_Number DESC;
            """

    with Database() as db:
        results = db.execute(query, (rating_threshold,))
    return render_template("search_multiple_roles_results.html", results=results)


@queries_bp.route("/top_thriller_movies_boston", methods=["GET"])
def top_thriller_movies_boston():
    """Display the top 2 thriller movies in Boston based on rating."""

    # >>>> TODO 10: Find the top 2 rates thriller movies (genre is thriller) that were shot exclusively in Boston. <<<<
    #               This means that the movie cannot have any other shooting location. 
    #               List the `movie names` and their `ratings`.

    query = """ SELECT m.name AS Motion_Picture_Name, m.rating
                FROM MotionPicture m 
                JOIN Genre g ON g.mpid = m.id
                WHERE g.genre_name = "Thriller"
                ORDER BY m.rating DESC
                LIMIT 2;  """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_thriller_movies_boston.html", results=results)



@queries_bp.route("/search_movies_by_likes", methods=["POST"])
def search_movies_by_likes():
    """
    Search for movies that have received more than a specified number of likes,
    where the liking users are below a certain age.
    """
    min_likes = int(request.form["min_likes"])
    max_age = int(request.form["max_age"])

    # >>>> TODO 11: Find all the movies with more than “X” likes by users of age less than “Y”. <<<<
    #               List the movie names and the number of likes by those age-group users.

    query = """ SELECT mp.name, COUNT(DISTINCT l.uemail)
                FROM Movie m
                JOIN MotionPicture mp ON m.mpid = mp.id
                JOIN Likes l ON l.mpid = m.mpid
                JOIN Users u ON u.email = l.uemail
                WHERE u.age < %s
                GROUP BY m.mpid
                HAVING COUNT(DISTINCT l.uemail) > %s;
            """

    with Database() as db:
        results = db.execute(query, (max_age, min_likes))
    return render_template("search_movies_by_likes_results.html", results=results)


@queries_bp.route("/actors_marvel_warner", methods=["GET"])
def actors_marvel_warner():
    """
    List actors who have appeared in movies produced by both Marvel and Warner Bros.
    """

    # >>>> TODO 12: Find the actors who have played a role in both “Marvel” and “Warner Bros” productions. <<<<
    #               List the `actor names` and the corresponding `motion picture names`.

    query = """
                SELECT p.name AS Actor_Name, GROUP_CONCAT(m.name) AS Motion_Picture_Names
                FROM People p
                JOIN Role r ON p.id = r.pid
                JOIN MotionPicture m ON r.mpid = m.id
                GROUP BY p.id
                HAVING SUM(CASE WHEN r.role_name = 'Actor' THEN 1 ELSE 0 END) > 0
                AND COUNT(CASE WHEN m.production = 'Marvel' THEN m.production END) > 0
                AND COUNT(CASE WHEN m.production = 'Warner Bros' THEN m.production END) > 0; 
            
                """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_marvel_warner.html", results=results)


@queries_bp.route("/movies_higher_than_comedy_avg", methods=["GET"])
def movies_higher_than_comedy_avg():
    """
    Display movies whose rating is higher than the average rating of comedy movies.
    """

    # >>>> TODO 13: Find the motion pictures that have a higher rating than the average rating of all comedy (genre) motion pictures. <<<<
    #               Show the names and ratings in descending order of ratings.

    query = """ SELECT DISTINCT m.name, m.rating
                FROM MotionPicture m
                JOIN Genre g ON g.mpid = m.id
                WHERE m.rating > (
                    SELECT AVG(m.rating)
                    FROM MotionPicture m
                    JOIN Genre g ON g.mpid = m.id
                    WHERE g.genre_name = "Comedy" 
                )
                ORDER BY m.rating DESC;
                """

    with Database() as db:
        results = db.execute(query)
    return render_template("movies_higher_than_comedy_avg.html", results=results)


@queries_bp.route("/top_5_movies_people_roles", methods=["GET"])
def top_5_movies_people_roles():
    """
    Display the top 5 movies that involve the most people and roles.
    """

    # >>>> TODO 14: Find the top 5 movies with the highest number of people playing a role in that movie. <<<<
    #               Show the `movie name`, `people count` and `role count` for the movies.

    query = """  SELECT mp.name, COUNT(DISTINCT r.pid), COUNT(DISTINCT r.role_name)
                 FROM Movie m
                 JOIN MotionPicture mp ON mp.id = m.mpid
                 JOIN Role r ON r.mpid = m.mpid
                 JOIN People p ON p.id = r.pid
                 GROUP BY m.mpid
                 ORDER BY COUNT(DISTINCT r.pid) DESC
                 LIMIT 5;
            """

    with Database() as db:
        results = db.execute(query)
    return render_template("top_5_movies_people_roles.html", results=results)


@queries_bp.route("/actors_with_common_birthday", methods=["GET"])
def actors_with_common_birthday():
    """
    Find pairs of actors who share the same birthday.
    """

    # >>>> TODO 15: Find actors who share the same birthday. <<<<
    #               List the actor names (actor 1, actor 2) and their common birthday.

    query = """ SELECT p1.name AS actor1, p2.name AS actor2, p1.dob AS common_birthday
                FROM People p1
                JOIN People p2 ON p1.dob = p2.dob AND p1.id != p2.id
                JOIN Role r1 ON p1.id = r1.pid AND r1.role_name = 'Actor'
                JOIN Role r2 ON p2.id = r2.pid AND r2.role_name = 'Actor'
                GROUP BY p1.dob;
            """

    with Database() as db:
        results = db.execute(query)
    return render_template("actors_with_common_birthday.html", results=results)