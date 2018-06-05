function getFilterDefaults(index) {

  var cookieDict = {}
  var cookieEntries = document.cookie.split(";")
  for (var i = 0; i < cookieEntries.length; i++) {
    var cookieNv = cookieEntries[i].split("=")
    var cn = cookieNv[0].trim()
    var cl = cn.split(".")
    if (cl.length > 0) {
      if (cl[0] == index) {
        cookieDict[cl[1]] = cookieNv[1]
      }
    }
  }

  return cookieDict
}

function setFilterCookie(index, key, value) {
  var expiration_date = new Date();
  expiration_date.setFullYear(expiration_date.getFullYear() + 1);
  document.cookie = index + "." + key + "=" + value + "; path=/; expires=" + expiration_date.toUTCString();
}


function toTitleCase(str) {
  return str.replace(/\w\S*/g, function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  });
}

function candidateFilters(index,filters,refresh) {

  var data = {}
  data.filters = filters

  if (data.filters) {
    //if(newsearch){
    var filterBankHTML = ''
    //populate filter bank
    var nrows = Math.ceil(data.filters.length / 4)

    var j = 0
    for (var i = 0; i < nrows; i++) {
      filterBankHTML += '<div class="row">'
      for (var k = 0; k < 4; k++) {

        filterBankHTML += '<div class="col-sm-2 col-md-3 col-lg-3 text-center">'
        if (j < data.filters.length) {
          filterBankHTML += '<div id="filtGroup'
          filterBankHTML += j
          filterBankHTML += '" class="btn-group">'
          filterBankHTML += '<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false"'
          filterBankHTML += ' id="flt' + j
          filterBankHTML += '">'

          if (candidateIndexFilters[data.filters[j].IndexField]) {
            filterBankHTML += data.filters[j].IndexField + ":&nbsp<strong>" + toTitleCase(candidateIndexFilters[data.filters[j].IndexField] + "</strong>")
          } else {
            filterBankHTML += data.filters[j].IndexField
          }


          filterBankHTML += '</button>'
          filterBankHTML += '<div class="dropdown-menu" role="menu">'
          var crit = data.filters[j].IndexNames
          for (var m = 0; m < crit.length; m++) {

            filterBankHTML += '<a style="text-transform:capitalize" class="dropdown-item"'
            filterBankHTML += 'id="flt'
            filterBankHTML += j
            filterBankHTML += "-"
            filterBankHTML += m
            filterBankHTML += '" href="#">'
            filterBankHTML += toTitleCase(crit[m])
            filterBankHTML += '</a>'
          }
          if (data.filters[j].Clearable) {
            filterBankHTML += '<hr/>'
            filterBankHTML += '<a class="dropdown-item" id="clr'
            filterBankHTML += j
            filterBankHTML += '" href="#">Clear</a>'
          }

          filterBankHTML += '</div>'
          filterBankHTML += '</div>'
        }

        filterBankHTML += '</div>'
        j++
      }
      filterBankHTML += '</div>'
    }

    $("#filterbank").html(filterBankHTML)
    $("#filterson").html("")

    for (var j = 0; j < data.filters.length; j++) {
      var crit = data.filters[j].IndexNames
      for (var m = 0; m < crit.length; m++) {
        $("#flt" + j + "-" + m).off("click");
        $("#flt" + j + "-" + m).click({
          filt: j,
          name: data.filters[j].IndexField,
          crit: crit[m],
          level: data.filters[j].IndexLevel
        }, function(e) {
          //$("#flt" + e.data.filt).html(e.data.name + ":" + e.data.crit)
          candidateIndexFilters[e.data.name] = e.data.crit
          var bhtml = ""
          for (var key in candidateIndexFilters) {
            bhtml += key + "." + candidateIndexFilters[key] + "/"
          }
          //$("#filterson").html(bhtml)
          if (e.data.level < 3) {
            setFilterCookie(index, e.data.name, candidateIndexFilters[e.data.name])
          }

          //call positionSearch

          //if file or text, rerun search
          // if (searchType == "position") {
          //   positionSearch(false)
          // } else {
          //   refreshSimilarCandidates()
          // }

          refresh(false)


        })
        $("#clr" + j).off("click");
        $("#clr" + j).click({
          filt: j,
          name: data.filters[j].IndexField,
          level: data.filters[j].IndexLevel
        }, function(e) {
          $("#flt" + e.data.filt).html(e.data.name)
          delete candidateIndexFilters[e.data.name];
          var bhtml = ""
          for (var key in candidateIndexFilters) {
            bhtml += key + "." + candidateIndexFilters[key] + "/"
          }
          if (e.data.level < 3) {
            setFilterCookie(index, e.data.name, "")
          }
          //$("#filterson").html(bhtml)

          //if file or text, rerun search
          // if (searchType == "position") {
          //   positionSearch(false)
          // } else {
          //   refreshSimilarCandidates()
          // }

          refresh(false)

        })
      }
    }
  }

}
