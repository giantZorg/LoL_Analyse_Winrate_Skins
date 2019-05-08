###
# 
#
###

rm(list = ls())

setwd("F:")

# Pakete falls notwendig installieren und laden
pakete <- c("tcltk", "httr", "devtools", "zoo", "RColorBrewer", "stringr")
paketeGithub <- c() # Beispiel: paketeGithub <- c("giantZorg/cats")

libList <- installed.packages()
for (paket in pakete) {
	if (!(paket %in% libList)) {install.packages(paket, dependencies = TRUE)}
	library(paket, character.only = TRUE)
}

for (paket in paketeGithub) {
	anmeldungNotwendig <- TRUE

	paketOhnePfad <- strsplit(paket, '/')[[1]]
	paketOhnePfad <- paketOhnePfad[length(paketOhnePfad)]

	if (!(paket %in% libList)) {
		if (anmeldungNotwendig) {
			source("Analyse/Ressourcen/proxyOeffnen.R")
			proxyOeffnen()
			anmeldungNotwendig <- FALSE
		}
		install_github(paket, dependencies = TRUE)
	}
	library(paketOhnePfad, character.only = TRUE)
}

alphaHinzufuegen <- function(colors, alpha = 1.0) {
    r <- col2rgb(colors, alpha = T)
    # Apply alpha
    r[4,] <- alpha * 255
    r <- r / 255.0
    return(rgb(r[1,], r[2,], r[3,], r[4,]))
}


###
# Daten einlesen
beliebtheit <- read.csv("lol_champions_beliebtheit.csv")
bannrate <- read.csv("lol_champions_bannrate.csv")
winrate <- read.csv("lol_champions_winrate.csv")

patchDaten <- read.csv("lol_patch_daten.csv")

names(beliebtheit) <- c("Zeit", "Beliebtheit", "Champion")
names(bannrate) <- c("Zeit", "Bannrate", "Champion")
names(winrate) <- c("Zeit", "Winrate", "Champion")


# Anzahl Vorkommen in den Patchnotes
nPatchesBetrachtet <- dim(unique(patchDaten['Patchnummer']))[1]
verteilungHaeufigkeit <- sort(table(patchDaten[patchDaten['Typ'] == 'Champion', 4]), decreasing = TRUE)

dfVerteilungHaeufigkeit <- data.frame(verteilungHaeufigkeit)
nChamps <- dim(dfVerteilungHaeufigkeit)[1]

nColTabelle <- 5
nRowTabelle <- ceiling(nChamps / nColTabelle)

dfVerteilungHaeufigkeitUmgeformt <- data.frame(matrix(NA, nrow = nRowTabelle, ncol = nColTabelle * 2))
for (i in 1:nColTabelle) {
    dfVerteilungHaeufigkeitUmgeformt[,c(2*i-1, 2*i)] <- dfVerteilungHaeufigkeit[((i-1)*nRowTabelle+1):(i*nRowTabelle),]
}

write.csv(dfVerteilungHaeufigkeit, "lol_verteilung_champion_patches.csv", row.names = FALSE)
write.csv(dfVerteilungHaeufigkeitUmgeformt, "lol_verteilung_champion_patches_umgeformt.csv", row.names = FALSE)


###
# Plot Anzahl Skins/Championänderungen über den Verlauf der Patches
vorhandenePatches <- unique(patchDaten$Patchnummer)
nPatches <- length(vorhandenePatches)

patchZeiten <- as.Date(patchDaten$Patchdatum[match(vorhandenePatches, patchDaten$Patchnummer)], format = "%d.%m.%Y")

nChampAenderungenProPatch <- nSkinsProPatch <- vector("numeric", nPatches)

for (i in 1:nPatches) {
    patchAuswahl <- patchDaten[patchDaten$Patchnummer == vorhandenePatches[i],]
    nChampAenderungenProPatch[i] <- sum(patchAuswahl$Typ == "Champion")
    nSkinsProPatch[i] <- sum(patchAuswahl$Typ == "Skins")
}

smSplinesChampsCV <- smooth.spline(1:nPatches, nChampAenderungenProPatch, cv = TRUE) #df = 9.3
smSplinesChamps <- smooth.spline(1:nPatches, nChampAenderungenProPatch, df = 9.3)

smSplinesSkinsCV <- smooth.spline(1:nPatches, nSkinsProPatch, cv = TRUE) #df = 13.3
smSplinesSkins <- smooth.spline(1:nPatches, nSkinsProPatch, df = 13.3)

xAchsePatchesLabels <- c("4.11", "5.1", "5.11", "6.1", "6.11", "7.1", "7.11", "8.1", "8.11", "9.1", "9.9")
xAchsePatches <- match(xAchsePatchesLabels, vorhandenePatches)

# Graph Championanpassungen
png("lol_patch_championanpassungen.png", width = 1000, height = 600, res = 100)
plot(1:nPatches, nChampAenderungenProPatch, xaxt = "n", xlab = "Patch", ylab = "Number of champion changes")
lines(smSplinesChamps$x, smSplinesChamps$y, lwd = 2, col = "red")
axis(1, at = xAchsePatches, labels = xAchsePatchesLabels)
dev.off()

# Graph Skinanpassungen
png("lol_patch_skins_und_chromas.png", width = 1000, height = 600, res = 100)
plot(1:nPatches, nSkinsProPatch, xaxt = "n", xlab = "Patch", ylab = "Number of released skins and chromas")
lines(smSplinesSkins$x, smSplinesSkins$y, lwd = 2, col = "red")
axis(1, at = xAchsePatches, labels = xAchsePatchesLabels)
dev.off()

# Vergleich Champions/Skins
png("lol_patch_vergleich_champ_skins.png", width = 1200, height = 600, res = 100)
par(mfrow = c(1,2))
plot(smSplinesChamps$x, smSplinesChamps$y, lwd = 2, col = "red", type = "l", ylim = c(0, 20), xaxt = "n", xlab = "Patch", ylab = "Number of changes/skins")
lines(smSplinesSkins$x, smSplinesSkins$y, lwd = 2, col = "blue")
axis(1, at = xAchsePatches, labels = xAchsePatchesLabels)
legend("right", legend = c("Champion changes", "Skins and chromas"), col = c("red", "blue"), lwd = 2)

plot(smSplinesChamps$x, smSplinesChamps$y / max(smSplinesChamps$y), lwd = 2, col = "red", type = "l", ylim = c(0, 1), xaxt = "n", xlab = "Patch", ylab = "Number of changes/skins normalized")
lines(smSplinesSkins$x, smSplinesSkins$y / max(smSplinesSkins$y), lwd = 2, col = "blue")
axis(1, at = xAchsePatches, labels = xAchsePatchesLabels)
legend("bottomright", legend = c("Champion changes", "Skins and chromas"), col = c("red", "blue"), lwd = 2)
dev.off()

korrelation <- cor(nChampAenderungenProPatch, nSkinsProPatch) # -0.12
png("lol_ccf_champion_changes_skins.png", width = 1000, height = 600, res = 100)
ccf(nSkinsProPatch, nChampAenderungenProPatch, main = "") # The lag k value returned by ccf(x, y) estimates the correlation between x[t+k] and y[t]
dev.off()
# -> Wenn viele Championänderungen, dann gibt es 6 Patches später auch viele Skins
# -> Wenn viele Championänderungen, dann gab es vor 5-6 Patches eher weniger Skins


###
# Daten nach Champions sortieren
datenKombiniert <- vector("list", nChamps)
champListe <- unique(beliebtheit$Champion)

for (i in 1:nChamps) {
    dfBeliebtheit <- beliebtheit[beliebtheit$Champion == champListe[i],]
    dfBannrate <- bannrate[bannrate$Champion == champListe[i],]
    dfWinrate <- winrate[winrate$Champion == champListe[i],]

    dfZusammen <- merge(dfBeliebtheit[, 1:2], dfBannrate[, 1:2], by = "Zeit")
    dfZusammen <- merge(dfZusammen, dfWinrate[1:2], by = "Zeit")

    dfZusammen['ZeitKonvertiert'] <- sapply(dfZusammen['Zeit'], as.Date)

    datenKombiniert[[i]] <- dfZusammen
}
names(datenKombiniert) <- champListe

# Daten nach Patches sortieren
datenPatchesKombiniert <- vector("list", nPatches)

for (i in 1:nPatches) {
    datenPatchesKombiniert[[i]] <- vector("list", 2) # Champs und Skins getrennt
    patchAuswahl <- patchDaten[patchDaten$Patchnummer == vorhandenePatches[i],]

    datenPatchesKombiniert[[i]][[1]] <- patchAuswahl[patchAuswahl$Typ == "Champion",]$Champion
    datenPatchesKombiniert[[i]][[2]] <- patchAuswahl[patchAuswahl$Typ == "Skins",]$Champion
}


###
# Erster Graph: Hat ein Champ in den 1 bis 3 Patches, bevor er einen Skin bekommen hat, eine Änderung bekommen?
# Zweiter Graph: Hat sich die Winrate eines Champs 3 Wochen vor und 3 Wochen nach einem neuen Skin deutlich verändert? -> Boxplots

patchDiff <- 1:3    # Maximal betrachteter Lag für die Patches
datenGraphEins <- vector("list", length(patchDiff))

for (i in 1:length(patchDiff)) {
    nBetrachtetePatches <- nPatches - patchDiff[i]
    datenGraphEins[[i]] <- matrix(NA, nrow = nBetrachtetePatches, ncol = 2) # Erste Spalte: Anzahl Skins. Zweite Spalte: Anzahl mit Änderungen

    for (j in 1:nBetrachtetePatches) {
        neueSkins <- datenPatchesKombiniert[[j + patchDiff[i]]][[2]]

        datenGraphEins[[i]][j, 1] <- length(neueSkins)

        if (length(neueSkins)) {
            # Skinliste der letzten patchDiff[i] Patches erstellen
            champsVeraendertListe <- vector("list", patchDiff[i] + 1)
            for (k in 1:(patchDiff[i] + 1)) {
                champsVeraendertListe[[k]] <- datenPatchesKombiniert[[j + k - 1]][[1]]
            }
            champsVeraendert <- do.call("c", champsVeraendertListe)

            datenGraphEins[[i]][j, 2] <- sum(!is.na(match(neueSkins, champsVeraendert)))
        } else {
            datenGraphEins[[i]][j, 2] <- 0
        }
    }
}

zahlenVeraenderungenAnChampsVorSkins <- matrix(NA, nrow = length(patchDiff), ncol = 2)
for (i in 1:length(patchDiff)) {
    zahlenVeraenderungenAnChampsVorSkins[i,] <- apply(datenGraphEins[[i]], 2, sum)
}
przVeraenderungenAnChampsVorSkins <- zahlenVeraenderungenAnChampsVorSkins[, 2] / zahlenVeraenderungenAnChampsVorSkins[, 1]

colPalette <- brewer.pal(3, "YlGnBu")
png("lol_champion_aenderung_vorhanden.png", width = 600, height = 400, res = 90)
bp <- barplot(zahlenVeraenderungenAnChampsVorSkins[, 1], col = alphaHinzufuegen(colPalette[1], 0.6), names.arg = patchDiff, xlab = "Number of considered past patches", ylab = "Number of skins")
barplot(zahlenVeraenderungenAnChampsVorSkins[, 2], add = TRUE, col = alphaHinzufuegen(colPalette[3], 0.6), names.arg = rep("", length(patchDiff)))
text(bp, zahlenVeraenderungenAnChampsVorSkins[, 2] + 25, labels = sapply(round(przVeraenderungenAnChampsVorSkins * 100), function(x) paste0(as.character(x), "%")))
dev.off()

# Zweiter Graph
nSkinsBetrachtet <- 0
for (i in 1:(nPatches-1)) {
    nSkinsBetrachtet <- nSkinsBetrachtet + length(datenPatchesKombiniert[[i]][[2]])
}

aenderungWinrateMitPatch <- matrix(NA, nrow = nSkinsBetrachtet, ncol = 3)
deltaTage <- 20
ct <- 1

for (i in 1:(nPatches - 1)) { # Keine neuen Daten für den letzten Patch
    neueSkins <- datenPatchesKombiniert[[i]][[2]]

    if (length(neueSkins)) {
        for (j in 1:length(neueSkins)) {
            datenChampion <- datenKombiniert[[match(neueSkins[j], champListe)]]

            if (min(datenChampion$ZeitKonvertiert) < (patchZeiten[i] - deltaTage)) {
                aenderungWinrateMitPatch[ct, 1] <- approx(datenChampion$ZeitKonvertiert, datenChampion$Winrate, patchZeiten[i] - deltaTage)$y
                aenderungWinrateMitPatch[ct, 2] <- approx(datenChampion$ZeitKonvertiert, datenChampion$Winrate, min(patchZeiten[i] + deltaTage, max(datenChampion$ZeitKonvertiert)))$y

                aenderungWinrateMitPatch[ct, 3] <- as.integer(strsplit(vorhandenePatches[i], '[.]')[[1]][1])

                ct <- ct + 1
            }
        }
    }
}

aenderungWinrateMitPatch <- aenderungWinrateMitPatch[1:(ct - 1),]

png("lol_boxplot_aenderung_winrate.png", width = 400, height = 400, res = 100)
par(mar = c(2,4,2,2) + 0.1)
boxplot(aenderungWinrateMitPatch[, 2] - aenderungWinrateMitPatch[, 1], ylab = "Change in winrate")
dev.off()

summary(aenderungWinrateMitPatch[, 2] - aenderungWinrateMitPatch[, 1])
#    Min.  1st Qu.   Median     Mean  3rd Qu.     Max. 
#- 8.11151 - 0.82996 0.01702 - 0.02305 0.75767 10.25863

png("lol_boxplot_aenderung_winrate_seasons.png", width = 800, height = 540, res = 100)
par(mar = c(5,4,2,2) + 0.1)
boxplot(aenderungWinrateMitPatch[, 2] - aenderungWinrateMitPatch[, 1] ~ aenderungWinrateMitPatch[, 3], xlab = "", ylab = "", xaxt = "n", yaxt = "n")
abline(h = 0, lwd = 2, col = "red")
boxplot(aenderungWinrateMitPatch[, 2] - aenderungWinrateMitPatch[, 1] ~ aenderungWinrateMitPatch[, 3], ylab = "Change in winrate", xlab = "Season", add = TRUE)
dev.off()



