import requests
from bs4 import BeautifulSoup
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Movie
from .serializers import MovieSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status

class MovieSearchView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        """POST orqali kinolarni qidirish"""
        data = request.data
        query = data.get("query", "")

        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Bazadan qidirish
        movie = Movie.objects.filter(Q(title__iexact=query) | Q(title__icontains=query)).first()
        if movie:
            serializer = MovieSerializer(movie)
            return Response({**serializer.data, "source": "database"}, status=status.HTTP_200_OK)

        # Veb sahifadan qidirish
        search_url = f"https://www.kinopoisk.ru/index.php?kp_query={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            return Response({"error": "Kinoni qidirishda xatolik!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        soup = BeautifulSoup(response.text, "html.parser")
        movie_element = soup.find("div", class_="element")

        if not movie_element:
            return Response({"error": "Film topilmadi!"}, status=status.HTTP_404_NOT_FOUND)

        # Ma'lumotlarni olish
        title = movie_element.find("p", class_="name").text.strip()
        year = movie_element.find("span", class_="year").text.strip()
        link = "https://www.kinopoisk.ru/" + movie_element.find("a")["href"]

        # Bazaga saqlash
        new_movie = Movie.objects.create(title=title, year=year, link=link)

        return Response({
            "title": new_movie.title,
            "year": new_movie.year,
            "link": new_movie.link,
            "source": "web"
        }, status=status.HTTP_201_CREATED)

    def get(self, request):
        """GET orqali kinolarni qidirish"""
        query = request.GET.get("q")
        if not query:
            return Response({"error": "Qidiruv so‘zi kerak!"}, status=status.HTTP_400_BAD_REQUEST)

        # Bazadan qidirish
        movie = Movie.objects.filter(Q(title__iexact=query) | Q(title__icontains=query)).first()
        if movie:
            serializer = MovieSerializer(movie)
            return Response({**serializer.data, "source": "database"}, status=status.HTTP_200_OK)

        return Response({"error": "Film topilmadi!"}, status=status.HTTP_404_NOT_FOUND)
